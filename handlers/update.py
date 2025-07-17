"""
UpdateCommitHandler: Handles POST updates to commit metadata.

Supports in-memory editing of 'issue' and 'release' fields and writes changes
back to the spreadsheet using an atomic Excel save.
"""
import logging
from pathlib import Path

from tornado.web import HTTPError, RequestHandler

from utils.data import atomic_save_excel, get_row_index_by_sha


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
