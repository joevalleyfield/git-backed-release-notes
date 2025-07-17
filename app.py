"""
Git Viewer MVP

A minimal Tornado web app for browsing Git history with release-note annotations.
Loads commit metadata from an Excel file and links each commit to a detailed view
with `git show` output and surrounding tag context.

Usage:
    python app.py path/to/commits.xlsx --repo path/to/git/repo --tag-pattern "rel-*"
"""

import argparse

import logging
import os
from pathlib import Path

from tempfile import NamedTemporaryFile


import pandas as pd
from tornado.web import Application, HTTPError, RequestHandler
from tornado.ioloop import IOLoop

from handlers.commit import CommitHandler
from handlers.main import MainHandler

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())  # safe default


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
