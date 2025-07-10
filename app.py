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
import re
import subprocess
from types import SimpleNamespace

import pandas as pd
from tornado.web import Application, RequestHandler
from tornado.ioloop import IOLoop


class MainHandler(RequestHandler):
    """Serves the main page showing a table of commits loaded from the spreadsheet."""

    df: pd.DataFrame

    def initialize(self, df):
        """Inject the preloaded DataFrame of commit metadata into the handler."""
        self.df = df

    def data_received(self, chunk):
        pass  # Required by base class, not used

    def get(self):
        """
        Render the main commit table view.

        Passes the full commit metadata DataFrame (as a list of dicts) to the template
        for rendering as an interactive HTML table.
        """
        self.render("index.html", rows=self.df.to_dict(orient="records"))


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

            m = re.match(r"(.+)-(\d+)-g([0-9a-f]{7,})", raw)
            if m:
                base_tag, count, _ = m.groups()
                tag_sha = subprocess.run(
                    ["git", "rev-list", "-n", "1", base_tag],
                    capture_output=True,
                    text=True,
                    cwd=self.repo_path,
                    check=True,
                ).stdout.strip()

                return SimpleNamespace(
                    raw=raw, base_tag=base_tag, count=int(count), tag_sha=tag_sha
                )
            else:
                # Directly tagged
                tag_sha = subprocess.run(
                    ["git", "rev-list", "-n", "1", raw],
                    capture_output=True,
                    text=True,
                    cwd=self.repo_path,
                    check=True,
                ).stdout.strip()

                return SimpleNamespace(raw=raw, base_tag=raw, count=0, tag_sha=tag_sha)
        except subprocess.CalledProcessError:
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

            tag_shas = {
                line.split()[1]: line.split()[0]
                for line in tag_lines
                if fnmatch.fnmatch(
                    line.split()[0], self.application.settings["tag_pattern"]
                )
            }

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

            try:
                i = rev_list.index(sha)
            except ValueError:
                return None

            for descendant_sha in rev_list[i + 1 :]:
                if descendant_sha in tag_shas:
                    tag = tag_shas[descendant_sha]
                    return SimpleNamespace(base_tag=tag, tag_sha=descendant_sha)
        except subprocess.SubprocessError:
            # Likely due to tag lookup or invalid rev-list index
            return None

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
            (r"/", MainHandler, dict(df=df)),
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
        "excel_path", help="Path to the .xlsx file containing commit data"
    )
    parser.add_argument(
        "--repo",
        default=".",
        help="Path to the Git repository (default: current directory)",
    )
    parser.add_argument(
        "--tag-pattern", default="rel-*", help="Pattern for release tags"
    )
    args = parser.parse_args()

    df = pd.read_excel(args.excel_path).fillna("")

    app = make_app(df, args.repo, args.tag_pattern)
    app.listen(8888)
    print("Server running at http://localhost:8888")
    IOLoop.current().start()


if __name__ == "__main__":
    main()
