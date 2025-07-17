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

import pandas as pd
from tornado.web import Application
from tornado.ioloop import IOLoop

from handlers.commit import CommitHandler
from handlers.main import MainHandler
from handlers.update import UpdateCommitHandler

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
