"""
UpdateCommitHandler: Handles POST updates to commit metadata.

Supports in-memory editing of 'issue' and 'release' fields and writes changes
back to the spreadsheet using an atomic Excel save.
"""

import logging

from tornado.web import HTTPError, RequestHandler

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
        - 204 on successful update via AJAX request (no redirect)
        """

        # handlers/update.py (inside post)
        is_ajax = self.request.headers.get("X-Requested-With") == "fetch" or self.get_argument("ajax", None)

        store = self.application.settings.get("commit_metadata_store")
        if store is None:
            raise HTTPError(500, "No commit metadata store configured")

        try:
            if "issue" in self.request.body_arguments:
                new_issue = self.get_argument("issue", "").strip()
                store.set_issue(sha, new_issue)

            if "release" in self.request.body_arguments:
                new_release = self.get_argument("release", "").strip()
                store.set_release(sha, new_release)

            store.save()

        except KeyError as e:
            raise HTTPError(404, str(e)) from e

        if is_ajax:
            self.set_status(204)
            return

        next_url = self.get_argument("next", default=None)
        if next_url:
            self.redirect(next_url)
        else:
            self.redirect(f"/commit/{sha}")

    def data_received(self, chunk):
        pass  # Required by base class, not used
