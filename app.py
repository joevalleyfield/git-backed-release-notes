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
import re
import subprocess
from types import SimpleNamespace

import pandas as pd
from tornado.web import Application, RequestHandler
from tornado.ioloop import IOLoop

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())  # safe default


class MainHandler(RequestHandler):
    """Serves the main page showing a table of commits loaded from the spreadsheet."""

    df: pd.DataFrame
    repo_path: str

    def initialize(self, df, repo_path):
        """Inject the preloaded DataFrame of commit metadata into the handler."""
        self.df = df
        self.repo_path = repo_path

    def data_received(self, chunk):
        pass  # Required by base class, not used

    def get(self):
        """
        Render the main commit table view.

        Passes the full commit metadata DataFrame (as a list of dicts) to the template
        for rendering as an interactive HTML table.
        """
        if self.df is not None:
            rows = self.df.to_dict(orient="records")
        else:
            rows = extract_commits_from_git(self.repo_path)  # <- you must define this

        self.render("index.html", rows=rows)


def extract_commits_from_git(repo_path: str) -> list[dict]:
    """
    Extract commit metadata directly from the Git repository.

    Returns a list of dictionaries with keys: id, sha, release, message, and author_date.
    Used when no spreadsheet is provided.
    """
    result = subprocess.run(
        ["git", "-C", repo_path, "log", "--pretty=format:%H%x09%ad%x09%s", "--date=iso"],
        capture_output=True,
        text=True,
        check=True,
    )

    rows = []
    for idx, line in enumerate(result.stdout.strip().splitlines()):
        sha, author_date, message = line.split("\t", 2)
        rows.append({
            "id": idx,
            "sha": sha,
            "release": "",  # no spreadsheet = no release label
            "message": message,
            "author_date": author_date,
        })
    return rows


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

                    is_ancestor = subprocess.run(
                        ["git", "merge-base", "--is-ancestor", descendant_sha, sha],
                        cwd=self.repo_path,
                        check=False,
                    ).returncode == 0

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

        self.render(
            "commit.html", sha=sha, output=output, follows=follows, precedes=precedes
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


def make_app(df, repo_path, tag_pattern):
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
        ],
        template_path="templates",
        debug=True,
        tag_pattern=tag_pattern,
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
        "--port", type=int, default=8000,
        help="Port to run the server on (default: 8000)"
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

    app = make_app(df, args.repo, args.tag_pattern)
    app.listen(args.port)
    print("Server running at http://localhost:8888", flush=True)

    IOLoop.current().start()


if __name__ == "__main__":
    main()
