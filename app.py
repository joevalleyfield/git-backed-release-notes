"""
Git Viewer MVP

A minimal Tornado web app for browsing Git history with release-note annotations.
Loads commit metadata from an Excel file and links each commit to a detailed view
with `git show` output and surrounding tag context.

Usage:
    python app.py path/to/commits.xlsx --repo path/to/git/repo --tag-pattern "rel-*"
"""

import argparse
import fnmatch
import logging
import os
from pathlib import Path
import re
import subprocess
from tempfile import NamedTemporaryFile
from types import SimpleNamespace

import pandas as pd
from tornado.web import Application, HTTPError, RequestHandler
from tornado.ioloop import IOLoop

from handlers.main import MainHandler

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())  # safe default


class CommitHandler(RequestHandler):
    """Serves detailed information about a single commit using `git show` and tag context."""

    repo_path: str

    def initialize(self, repo_path):
        """Store the repo path for subprocess calls to Git."""
        self.repo_path = repo_path

    def data_received(self, chunk):
        pass  # Required by base class, not used

    def find_closest_tags(self, sha):
        """
        Combine `follows` and `precedes` lookups into a single call.
        Returns a tuple: (follows_info, precedes_info)
        """
        follows = self.find_follows_tag(sha)
        precedes = self.find_precedes_tag(sha)
        return follows, precedes

    def find_follows_tag(self, sha):
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
                cwd=self.repo_path,
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
                    cwd=self.repo_path,
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

    def find_precedes_tag(self, sha):
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
                    cwd=self.repo_path,
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
                        cwd=self.repo_path,
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
                    cwd=self.repo_path,
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
                            cwd=self.repo_path,
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
        try:
            result = subprocess.run(
                ["git", "show", sha],
                capture_output=True,
                text=True,
                check=True,
                cwd=self.repo_path,
            )
            output = result.stdout
        except subprocess.CalledProcessError as e:
            output = f"Error running git show: {e}"

        follows, precedes = self.find_closest_tags(sha)
        df = self.application.settings["df"]
        commit_row = None
        if df is not None:
            df = self.application.settings["df"]
            matches = df[df["sha"] == sha]
            if not matches.empty:
                commit_row = matches.iloc[0].to_dict()

        self.render(
            "commit.html",
            sha=sha,
            output=output,
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


class UpdateCommitHandler(RequestHandler):
    """Handles updates to commit metadata submitted via POST."""

    def post(self, sha):
        """
        Update the 'issue' field for a commit in the spreadsheet.

        Expects a form field named 'issue' and a valid commit SHA in the URL.
        Locates the corresponding row in the loaded spreadsheet, updates the
        'issue' field in-memory, and overwrites the spreadsheet on disk.

        Responds with:
        - 500 if no spreadsheet is loaded
        - 404 if the SHA is not found in the spreadsheet
        - 302 redirect back to the commit detail page on success
        """

        df = self.application.settings["df"]
        if df is None:
            raise HTTPError(500, "No spreadsheet loaded")

        row_idx = get_row_index_by_sha(df, sha)
        if row_idx is None:
            raise HTTPError(404, f"No spreadsheet row found for commit {sha}")

        if "issue" in self.request.body_arguments:
            new_issue = self.get_argument("issue", "").strip()
            df.at[row_idx, "issue"] = new_issue

        if "release" in self.request.body_arguments:
            new_release = self.get_argument("release", "").strip()
            df.at[row_idx, "release"] = new_release

        xlsx_path = Path(self.application.settings.get("excel_path"))
        if xlsx_path:
            atomic_save_excel(df, xlsx_path)
        else:
            logger.warning("Edit applied in memory, but no excel_path set—changes not saved.")

        self.redirect(f"/commit/{sha}")

    def data_received(self, chunk):
        pass  # Required by base class, not used


def get_row_index_by_sha(df: pd.DataFrame, sha: str) -> int | None:
    """
    Return the index of the commit with the given SHA, or None if not found.
    """
    matches = df[df["sha"] == sha]
    if not matches.empty:
        return matches.index[0]
    return None


def atomic_save_excel(df: pd.DataFrame, path: Path):
    """
    Atomically save a DataFrame to an Excel file.

    Writes the DataFrame to a temporary file in the same directory as `path`, then
    replaces the original file using `os.replace()` for atomicity.

    By creating the temp file in the target directory, we ensure it's on the same
    filesystem, avoiding issues with cross-device replacements. Symlinked paths or
    nonstandard mounts could still violate this assumption.
    """
    with NamedTemporaryFile("wb", dir=path.parent, delete=False) as tmp:
        tmp_path = Path(tmp.name)
        df.to_excel(tmp_path, index=False)
    os.replace(tmp_path, path)  # Atomic if on same filesystem


def make_app(df, repo_path, tag_pattern, excel_path):
    """
    Create and return the Tornado application.

    Args:
        df (pd.DataFrame): The commit metadata loaded from Excel.
        repo_path (str): Path to the local Git repository.
        tag_pattern (str): Glob pattern to filter relevant tags (e.g. 'rel-*').
    """
    return Application(
        [
            (r"/", MainHandler, dict(df=df, repo_path=repo_path)),
            (r"/commit/([a-f0-9]+)", CommitHandler, dict(repo_path=repo_path)),
            (r"/commit/([a-f0-9]+)/update", UpdateCommitHandler),
        ],
        template_path="templates",
        debug=True,
        tag_pattern=tag_pattern,
        df=df,
        excel_path=excel_path,
    )


def main():
    """
    Parse CLI arguments, load the commit data, and launch the Tornado server.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--excel-path",
        type=str,
        default=None,
        help="Optional path to the remediation Excel spreadsheet",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to run the server on (default: 8000)",
    )
    parser.add_argument(
        "--repo",
        default=".",
        help="Path to the Git repository (default: current directory)",
    )
    parser.add_argument(
        "--tag-pattern", default="rel-*", help="Pattern for release tags"
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    args = parser.parse_args()
    if args.debug:
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)

    if args.excel_path:
        df = pd.read_excel(args.excel_path).fillna("")
    else:
        df = None

    app = make_app(df, args.repo, args.tag_pattern, excel_path=args.excel_path)
    app.listen(args.port)
    print(f"Server running at http://localhost:{args.port}", flush=True)

    IOLoop.current().start()


if __name__ == "__main__":
    main()
