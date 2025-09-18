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
from pathlib import Path
import time
import webbrowser

import pandas as pd
from tornado.web import Application
from tornado.ioloop import IOLoop

from handlers.commit import CommitHandler, CommitResolveHandler
from handlers.debug import GitStatsHandler
from handlers.issue import IssueDetailHandler, IssueUpdateHandler
from handlers.main import MainHandler
from handlers.update import UpdateCommitHandler

from utils.metadata_store import (
    SpreadsheetCommitMetadataStore,
    DataFrameCommitMetadataStore,
)

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())  # safe default


def make_app(df, repo_path, tag_pattern, excel_path):
    """
    Create and return the Tornado application.

    Args:
        df (pd.DataFrame): The commit metadata loaded from Excel.
        repo_path (str): Path to the local Git repository.
        tag_pattern (str): Glob pattern to filter relevant tags (e.g. 'rel-*').
    """
    if df is not None:
        store = SpreadsheetCommitMetadataStore(df, excel_path)
    else:
        store = DataFrameCommitMetadataStore(repo_path / "git-view.metadata.csv")

    return Application(
        [
            (r"/", MainHandler),
            (r"/commit/([a-f0-9]{40})/update", UpdateCommitHandler),
            (r"/commit/([a-f0-9]{40})", CommitHandler),
            (r"/commit/([^/]+)", CommitResolveHandler),
            (r"/issue/([^/]+)/update", IssueUpdateHandler),
            (r"/issue/([^/]+)", IssueDetailHandler),
            (r"/_debug/git-stats", GitStatsHandler),
        ],
        template_path="templates",
        debug=True,
        tag_pattern=tag_pattern,
        excel_path=excel_path,
        commit_metadata_store=store,
        issues_dir=repo_path / "issues",
        repo_path=repo_path,
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
    parser.add_argument("--no-browser", action="store_true")
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

    app = make_app(df, Path(args.repo), args.tag_pattern, excel_path=args.excel_path)
    app.listen(args.port)
    url = f"http://localhost:{args.port}"
    print(f"Server running at {url}", flush=True)
    if not args.no_browser:
        time.sleep(0.25)
        webbrowser.open(url)

    IOLoop.current().start()


if __name__ == "__main__":
    main()
