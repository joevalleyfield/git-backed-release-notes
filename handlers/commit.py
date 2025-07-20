"""
CommitHandler: Renders commit detail views with git show and tag context.

Includes logic for locating the nearest release tags before and after a given
commit using `git describe`, `rev-list`, and `merge-base`.
"""

import fnmatch
import logging
import re
import subprocess
from types import SimpleNamespace

from tornado.web import  RequestHandler

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())  # safe default


class CommitHandler(RequestHandler):
    """Serves detailed information about a single commit using `git show` and tag context."""

    def data_received(self, chunk):
        pass  # Required by base class, not used

    def find_closest_tags(self, repo_path, sha):
        """
        Combine `follows` and `precedes` lookups into a single call.
        Returns a tuple: (follows_info, precedes_info)
        """
        follows = self.find_follows_tag(repo_path, sha)
        precedes = self.find_precedes_tag(repo_path, sha)
        return follows, precedes

    def find_follows_tag(self, repo_path, sha):
        """
        Return the nearest matching tag reachable from the given commit using `git describe`.

        Returns:
            SimpleNamespace with fields:
            - raw: full describe string
            - base_tag: tag name
            - count: commits since tag
            - tag_sha: SHA of the base tag's commit
        """
        logger.debug("Resolving Follows tag for commit: %s", sha)
        try:
            result = subprocess.run(
                [
                    "git",
                    "describe",
                    "--tags",
                    "--match",
                    self.application.settings["tag_pattern"],
                    sha,
                ],
                capture_output=True,
                text=True,
                cwd=repo_path,
                check=True,
            )
            raw = result.stdout.strip()

            m: re.Match[str] | None = re.match(r"(.+)-(\d+)-g([0-9a-f]{7,})", raw)
            if m:
                base_tag, count, _ = m.groups()
                tag_sha = subprocess.run(
                    ["git", "rev-list", "-n", "1", base_tag],
                    capture_output=True,
                    text=True,
                    cwd=repo_path,
                    check=True,
                ).stdout.strip()

                logger.debug(
                    "Parsed describe output: base_tag=%s, count=%s", base_tag, count
                )
                logger.debug(
                    "Resolved base_tag '%s' to commit SHA: %s", base_tag, tag_sha
                )

                return SimpleNamespace(
                    raw=raw, base_tag=base_tag, count=int(count), tag_sha=tag_sha
                )
            else:
                # Directly tagged
                logger.debug(
                    "Commit %s is directly tagged with '%s'; omitting Follows", sha, raw
                )
                return SimpleNamespace(
                    raw=raw, base_tag=raw, count=0, tag_sha=sha  # The commit itself
                )

        except subprocess.CalledProcessError as e:
            logger.debug("git describe failed for commit %s: %s", sha, e)
            return None

    def find_precedes_tag(self, repo_path, sha):
        """
        Walks the topological order of commits forward from the given SHA,
        returning the first descendant that matches the tag pattern.

        Returns:
            SimpleNamespace with:
            - base_tag: tag name
            - tag_sha: SHA of the tag's commit
        """
        logger.debug("Resolving Precedes tag for commit: %s", sha)

        try:
            tag_lines = (
                subprocess.run(
                    [
                        "git",
                        "for-each-ref",
                        "--format=%(refname:strip=2) %(objectname)",
                        "refs/tags",
                    ],
                    capture_output=True,
                    text=True,
                    cwd=repo_path,
                    check=True,
                )
                .stdout.strip()
                .splitlines()
            )

            pattern = self.application.settings["tag_pattern"]
            # tag_shas = {
            #     line.split()[1]: line.split()[0]
            #     for line in tag_lines
            #     if fnmatch.fnmatch(line.split()[0], pattern)
            # }

            # Map tag name -> SHA of the *commit* the tag refers to
            tag_shas = {}
            for line in tag_lines:
                parts = line.split()
                tag_name = parts[0]
                if fnmatch.fnmatch(tag_name, pattern):
                    tag_commit_sha = subprocess.run(
                        ["git", "rev-list", "-n", "1", tag_name],
                        capture_output=True,
                        text=True,
                        cwd=repo_path,
                        check=True,
                    ).stdout.strip()
                    tag_shas[tag_commit_sha] = tag_name

            logger.debug("Collected %d total tags", len(tag_lines))
            logger.debug(
                "Filtered %d matching tags for pattern '%s'",
                len(tag_shas),
                pattern,
            )

            for tag_commit_sha, tag in tag_shas.items():
                logger.debug("Available tag: %s -> %s", tag, tag_commit_sha)

            if not tag_shas:
                return None

            rev_list = (
                subprocess.run(
                    ["git", "rev-list", "--topo-order", "--reverse", "--all"],
                    capture_output=True,
                    text=True,
                    cwd=repo_path,
                    check=True,
                )
                .stdout.strip()
                .splitlines()
            )

            logger.debug("rev-list contains %d commits", len(rev_list))
            if sha not in rev_list:
                logger.debug(
                    "Commit %s not found in rev-list --topo-order --reverse", sha
                )

            try:
                i = rev_list.index(sha)
            except ValueError:
                return None

            for descendant_sha in rev_list[i + 1 :]:
                logger.debug("Checking descendant SHA: %s", descendant_sha)

                if descendant_sha in tag_shas:
                    # Verify this is truly a descendant, not an ancestor or unrelated
                    logger.debug(
                        "Running: git merge-base --is-ancestor %s %s",
                        descendant_sha,
                        sha,
                    )

                    is_ancestor = (
                        subprocess.run(
                            ["git", "merge-base", "--is-ancestor", descendant_sha, sha],
                            cwd=repo_path,
                            check=False,
                        ).returncode
                        == 0
                    )

                    if is_ancestor:
                        logger.debug(
                            "Skipping tag SHA %s — it's actually an ancestor of %s",
                            descendant_sha,
                            sha,
                        )
                        continue

                    tag = tag_shas[descendant_sha]
                    logger.debug(
                        "Found descendant tag: %s at SHA: %s", tag, descendant_sha
                    )

                    return SimpleNamespace(base_tag=tag, tag_sha=descendant_sha)

            logger.debug("No matching Precedes tag found for commit: %s", sha)

        except subprocess.SubprocessError as e:
            # Likely due to tag lookup or invalid rev-list index
            logger.debug(
                "Subprocess error during precedes resolution for %s: %s", sha, e
            )

        return None

    def get(self, sha):
        """
        Render the commit detail view for the given SHA, including:
        - `git show` output
        - Nearest previous and next tags matching the filter pattern
        """
        repo_path = self.application.settings["repo_path"]
        try:
            result = subprocess.run(
                ["git", "show", sha],
                capture_output=True,
                text=True,
                check=True,
                cwd=repo_path,
            )
            output = result.stdout
        except subprocess.CalledProcessError as e:
            output = f"Error running git show: {e}"

        follows, precedes = self.find_closest_tags(repo_path, sha)
        df = self.application.settings["df"]
        commit_row = None
        if df is not None:
            df = self.application.settings["df"]
            matches = df[df["sha"] == sha]
            if not matches.empty:
                commit_row = matches.iloc[0].to_dict()

        split_index = output.find("diff --git")
        if split_index == -1:
            output_diff = "(No diff found)"
            header = output.strip()
        else:
            header = output[:split_index].strip()
            output_diff = output[split_index:].strip()

        header = output[:split_index].strip()
        diff = output[split_index:].strip()

        self.render(
            "commit.html",
            sha=sha,
            output_header=header,
            output_diff=diff,
            follows=follows,
            precedes=precedes,
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
