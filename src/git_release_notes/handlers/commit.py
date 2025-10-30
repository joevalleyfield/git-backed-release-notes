"""
CommitHandler: Renders commit detail views with git show and tag context.

Includes logic for locating the nearest release tags before and after a given
commit using `git describe`, `rev-list`, and `merge-base`.
"""

import fnmatch
import logging
import math
import re
import subprocess
from typing import Optional

from tornado.web import HTTPError, RequestHandler

from ..utils.git import (
    find_follows_tag,
    find_precedes_tag,
    get_commit_parents_and_children,
    get_describe_name,
    run_git,
)
from ..utils.issue_suggestions import compute_issue_suggestion
from ..utils.release_suggestions import compute_release_suggestion

logger = logging.getLogger(__name__)


class CommitHandler(RequestHandler):
    """Serves detailed information about a single commit using `git show` and tag context."""

    repo_path: str

    def initialize(self):
        """Store the repo path for subprocess calls to Git."""
        self.repo_path = self.application.settings.get("repo_path")

    def data_received(self, chunk):
        pass  # Required by base class, not used

    def find_closest_tags(self, sha):
        """
        Combine `follows` and `precedes` lookups into a single call.
        Returns a tuple: (follows_info, precedes_info)
        """
        pattern = self.application.settings["tag_pattern"]
        follows = find_follows_tag(sha, self.repo_path, pattern)
        precedes = find_precedes_tag(sha, self.repo_path, pattern)
        return follows, precedes

    def get_describe_name(self, sha):
        pattern = self.application.settings["tag_pattern"]
        describe_name = get_describe_name(self.repo_path, sha, pattern)
        return describe_name

    def get(self, sha):
        """
        Render the commit detail view for the given SHA, including:
        - `git show` output
        - Nearest previous and next tags matching the filter pattern
        """
        try:
            result = run_git(self.repo_path, "show", sha, check=True)
            output = result.stdout
        except subprocess.CalledProcessError as e:
            logger.error("git show failed for %s: %s", sha, e.stderr)
            output = None
        except Exception:
            logger.exception("Unexpected error while running git show for %s", sha)
            output = None

        if not output:
            self.set_status(500)
            self.write("No output from git show; see logs for details.")
            return

        follows, precedes = self.find_closest_tags(sha)
        describe_name = self.get_describe_name(sha)

        parents, children = get_commit_parents_and_children(sha, self.repo_path)

        store = self.application.settings.get("commit_metadata_store")

        commit_row = None
        if store is not None:
            store.reload()
            commit_row = store.get_row(sha)

        if commit_row is None:
            commit_row = {"sha": sha, "issue": "", "release": ""}

        split_index = output.find("diff --git")
        if split_index == -1:
            output_diff = "(No diff found)"
            header = output.strip()
        else:
            header = output[:split_index].strip()
            output_diff = output[split_index:].strip()

        # Extract paths from diff headers like: diff --git a/foo.py b/foo.py
        diff_lines = output_diff.splitlines()
        paths = []

        for line in diff_lines:
            if line.startswith("diff --git"):
                match = re.match(r"diff --git a/(.*?) b/", line)
                if match:
                    paths.append(match.group(1))

        suggestion_result = compute_issue_suggestion(self.repo_path, header, touched_paths=paths)
        existing_issues = suggestion_result.existing_issues

        raw_issue = commit_row.get("issue", "")
        if isinstance(raw_issue, str):
            issue_value = raw_issue
        elif raw_issue is None:
            issue_value = ""
        elif isinstance(raw_issue, float) and math.isnan(raw_issue):
            issue_value = ""
        else:
            issue_value = str(raw_issue)
        commit_row["issue"] = issue_value
        issue_suggestion = None
        issue_suggestion_source: Optional[str] = None

        if suggestion_result.suggestion:
            issue_suggestion = suggestion_result.suggestion
            issue_suggestion_source = suggestion_result.suggestion_source

        issue_prefilled = False

        if not issue_value and issue_suggestion:
            issue_value = issue_suggestion
            issue_prefilled = True

        raw_release = commit_row.get("release", "")
        if isinstance(raw_release, str):
            release_value = raw_release.strip()
        elif raw_release is None:
            release_value = ""
        elif isinstance(raw_release, float):
            release_value = "" if math.isnan(raw_release) else str(raw_release)
        else:
            release_value = str(raw_release)
        commit_row["release"] = release_value

        release_result = compute_release_suggestion(
            self.repo_path,
            sha,
            current_release=release_value,
            precedes=precedes,
            tag_pattern=self.application.settings["tag_pattern"],
        )
        release_suggestion = release_result.suggestion
        release_suggestion_source = release_result.suggestion_source
        release_suggestion_label = release_suggestion_source.title() if release_suggestion_source else None

        self.render(
            "commit.html",
            sha=sha,
            output_header=header,
            output_diff=output_diff,
            follows=follows,
            precedes=precedes,
            describe_name=describe_name,
            parents=parents,
            children=children,
            commit=commit_row,
            linked_issues=existing_issues,
            issue_value=issue_value,
            issue_suggestion=issue_suggestion,
            issue_prefilled=issue_prefilled,
            issue_suggestion_source=issue_suggestion_source,
            release_value=release_value,
            release_suggestion=release_suggestion,
            release_suggestion_source=release_suggestion_source,
            release_suggestion_label=release_suggestion_label,
        )

    def tag_matches(self, tag):
        """
        Return True if the given tag name matches the user-provided pattern.

        Uses shell-style glob matching (e.g. 'rel-*') to determine whether the tag
        should be considered in the Follows/Precedes context.

        Args:
            tag: The name of the Git tag (e.g. 'rel-4-21').

        Returns:
            True if the tag matches the pattern; False otherwise.
        """
        return fnmatch.fnmatch(tag, self.application.settings["tag_pattern"])


class CommitResolveHandler(RequestHandler):
    """
    Tornado request handler that resolves arbitrary Git revisions
    (abbreviated SHA, branch name, tag, etc.) into a full commit SHA
    and redirects to the canonical /commit/<full_sha> URL.
    """

    def get(self, rev_input: str):
        """
        Handle GET /commit/<rev>.

        Resolves <rev> using `git rev-parse`, then redirects the client
        to /commit/<full_sha>. If the revision cannot be resolved, a 404
        is returned. Redirect is temporary (302) to avoid client-side
        caching during development.
        """

        # Git refname rules:
        # - Each pathname component (between slashes) is limited to 255 bytes.
        # - Our regex ([^/]+) forbids slashes, so we’re only ever dealing with a single component.
        # - Truncating to 255 ensures we never hand git an overlong ref and avoids DoS with huge inputs.
        # - If we later allow slashes in the matcher, bump this limit (e.g. 512 or 1024) to cover
        #   multiple path segments, but keep *some* cap in place for safety.
        rev = rev_input[:255]

        try:
            result = run_git(self.application.settings["repo_path"], "rev-parse", rev)
            full_sha = result.stdout.strip()
        except subprocess.CalledProcessError as err:
            raise HTTPError(404, f"Revision {rev_input} not found") from err

        self.redirect(f"/commit/{full_sha}", permanent=True)
