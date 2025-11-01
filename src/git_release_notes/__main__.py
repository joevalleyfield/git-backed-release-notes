"""Command-line entry point for git-release-notes."""

from __future__ import annotations

import argparse
import logging
import os
import signal
import time
import webbrowser
from pathlib import Path
from types import FrameType
from typing import Iterable

import pandas as pd
from tornado.ioloop import IOLoop
from tornado.web import Application

from .handlers.commit import CommitHandler, CommitResolveHandler
from .handlers.debug import GitStatsHandler
from .handlers.issue import IssueDetailHandler, IssueUpdateHandler
from .handlers.issue_index import IssueIndexHandler
from .handlers.main import MainHandler
from .handlers.update import UpdateCommitHandler
from .utils.metadata_store import (
    DataFrameCommitMetadataStore,
    SpreadsheetCommitMetadataStore,
)

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

PACKAGE_ROOT = Path(__file__).resolve().parent
TEMPLATE_DIR = PACKAGE_ROOT / "templates"


def _should_use_local_assets(env_value: str | None) -> bool:
    if not env_value:
        return False

    return env_value.strip().lower() in {"1", "true", "yes", "on"}


def _install_signal_handlers(
    loop: IOLoop, *, signals_to_handle: Iterable[int] | None = None
) -> None:
    """Arrange for the given loop to stop when termination signals arrive."""

    if signals_to_handle is None:
        candidate_signals = (signal.SIGINT, getattr(signal, "SIGTERM", None))
        signals_to_handle = tuple(sig for sig in candidate_signals if sig is not None)

    def _handle_signal(signum: int, _frame: FrameType | None) -> None:
        logger.info("Received signal %s; shutting down", signum)
        loop.add_callback_from_signal(loop.stop)

    for signum in signals_to_handle:
        signal.signal(signum, _handle_signal)


def _start_ioloop(loop: IOLoop) -> None:
    """Start the loop and ensure KeyboardInterrupt stops it cleanly."""

    try:
        loop.start()
    except KeyboardInterrupt:
        logger.info("Stopping Tornado IOLoop on Ctrl+C")
        loop.stop()


def make_app(
    df: pd.DataFrame | None,
    repo_path: Path,
    tag_pattern: str,
    excel_path: str | None,
    *,
    use_local_assets: bool | None = None,
) -> Application:
    """Create the Tornado application configured with handlers and settings."""

    if df is not None:
        store = SpreadsheetCommitMetadataStore(df, excel_path)
    else:
        store = DataFrameCommitMetadataStore(repo_path / "git-view.metadata.csv")

    if use_local_assets is None:
        use_local_assets = _should_use_local_assets(os.getenv("USE_LOCAL_ASSETS"))

    static_dir = PACKAGE_ROOT / "static"
    static_dir.mkdir(parents=True, exist_ok=True)

    return Application(
        [
            (r"/", MainHandler),
            (r"/commit/([a-f0-9]{40})/update", UpdateCommitHandler),
            (r"/commit/([a-f0-9]{40})", CommitHandler),
            (r"/commit/([^/]+)", CommitResolveHandler),
            (r"/issues", IssueIndexHandler),
            (r"/issue/([^/]+)/update", IssueUpdateHandler),
            (r"/issue/([^/]+)", IssueDetailHandler),
            (r"/_debug/git-stats", GitStatsHandler),
        ],
        template_path=str(TEMPLATE_DIR),
        debug=True,
        static_path=str(static_dir),
        static_url_prefix="/static/",
        tag_pattern=tag_pattern,
        excel_path=excel_path,
        commit_metadata_store=store,
        issues_dir=repo_path / "issues",
        repo_path=repo_path,
        use_local_assets=use_local_assets,
    )


def main() -> None:
    """Parse CLI arguments, prepare data sources, and launch the server."""

    parser = argparse.ArgumentParser(description="Run the git-release-notes UI")
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
    parser.add_argument("--tag-pattern", default="rel-*", help="Pattern for release tags")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    args = parser.parse_args()

    if args.debug:
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)

    df: pd.DataFrame | None

    if args.excel_path:
        df = pd.read_excel(args.excel_path).fillna("")
    else:
        df = None

    repo_path = Path(args.repo)
    app = make_app(df, repo_path, args.tag_pattern, excel_path=args.excel_path)
    app.listen(args.port)
    url = f"http://localhost:{args.port}"
    print(f"Server running at {url}", flush=True)
    print(f"  Commit index: {url}/", flush=True)
    print(f"  Issue index: {url}/issues", flush=True)

    if not args.no_browser:
        time.sleep(0.25)
        webbrowser.open(url)

    loop = IOLoop.current()
    _install_signal_handlers(loop)
    _start_ioloop(loop)


if __name__ == "__main__":
    main()
