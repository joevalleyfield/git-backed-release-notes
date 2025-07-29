"""
MainHandler: Serves the main page displaying a table of commits.

Renders commit metadata loaded from a spreadsheet or extracted directly from Git,
and passes it to the template for interactive browsing.
"""

import logging
import pandas as pd
from tornado.web import RequestHandler

from utils.git import extract_commits_from_git
from utils.metadata_store import CommitMetadataStore


logger = logging.getLogger(__name__)


class MainHandler(RequestHandler):
    """Serves the main page showing a table of commits loaded from the spreadsheet."""

    df: pd.DataFrame
    repo_path: str
    store: CommitMetadataStore

    def initialize(self):
        """Inject the preloaded DataFrame of commit metadata into the handler."""
        self.df = self.application.settings.get("df")
        self.repo_path = self.application.settings.get("repo_path")
        self.store = self.application.settings.get("commit_metadata_store")

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
            git_rows = extract_commits_from_git(self.repo_path)

            logger.info("Extracted %d git commits", len(git_rows))
            for row in git_rows:
                logger.info("GIT SHA: %s — %s", row["sha"], row["message"])

            metadata_df = self.store.df.fillna("")  # from DataFrameCommitMetadataStore

            if not metadata_df.empty:
                metadata = metadata_df.set_index("sha").to_dict(orient="index")
            else:
                metadata = {}

            logger.info("Metadata rows: %d", len(metadata_df))
            for sha in metadata_df["sha"]:
                logger.info("META SHA: %s", sha)

            # Merge
            rows = []
            for row in git_rows:
                sha = row["sha"]
                meta = metadata.get(sha, {})
                row["issue"] = meta.get("issue", "")
                row["release"] = meta.get("release", "")
                rows.append(row)

        self.render("index.html", rows=rows)
