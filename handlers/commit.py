"""
CommitHandler: Renders commit detail views with git show and tag context.

Includes logic for locating the nearest release tags before and after a given
commit using `git describe`, `rev-list`, and `merge-base`.
"""

import fnmatch
import logging
from pathlib import Path
import re
import subprocess

from tornado.web import RequestHandler

from utils.git import get_commit_parents_and_children, find_follows_tag, find_precedes_tag, get_describe_name
from utils.commit_parsing import extract_issue_slugs


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
            result = subprocess.run(
                ["git", "show", sha],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=True,
                cwd=self.repo_path,
            )
            output = result.stdout
        except subprocess.CalledProcessError as e:
            logger.error("git show failed for %s: %s", sha, e.stderr)
            output = None
        except Exception as e:
            logger.exception("Unexpected error while running git show")
            output = None

        if not output:
            self.set_status(500)
            self.write("No output from git show; see logs for details.")
            return

        follows, precedes = self.find_closest_tags(sha)
        describe_name = self.get_describe_name(sha)

        parents, children = get_commit_parents_and_children(sha, self.repo_path)

        df = self.application.settings.get("df")
        store = self.application.settings.get("commit_metadata_store")

        if df is not None:
            match = df[df["sha"] == sha]
        elif hasattr(store, "df"):
            match = store.df[store.df["sha"] == sha]
        else:
            match = None

        if match is not None and not match.empty:
            commit_row = match.iloc[0].fillna("").to_dict()
        else:
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
            
        primary_issue, slugs = extract_issue_slugs(header)
        existing_issues = []

        for slug in slugs:
            # Open and closed issues
            for subdir in ("open", "closed"):
                issue_path = self.repo_path / "issues" / subdir / f"{slug}.md"
                if issue_path.exists():
                    existing_issues.append(slug)
                    break  # Found in either location

        # Add slugs implied by touched issue files
        for path in paths:
            if path.startswith("issues/open/") or path.startswith("issues/closed/"):
                if path.endswith(".md"):
                    slug = Path(path).stem
                    if slug not in slugs:
                        existing_issues.append(slug)

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
            primary_issue=primary_issue if primary_issue in existing_issues else None,
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
