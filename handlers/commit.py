"""
CommitHandler: Renders commit detail views with git show and tag context.

Includes logic for locating the nearest release tags before and after a given
commit using `git describe`, `rev-list`, and `merge-base`.
"""

import fnmatch
import logging
import re
import subprocess

from tornado.web import RequestHandler

from utils.git import get_commit_parents_and_children, find_follows_tag, find_precedes_tag


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

        self.render(
            "commit.html",
            sha=sha,
            output_header=header,
            output_diff=output_diff,
            follows=follows,
            precedes=precedes,
            parents=parents,
            children=children,
            commit=commit_row,
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
