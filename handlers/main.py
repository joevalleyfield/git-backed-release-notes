"""
MainHandler: Serves the main page displaying a table of commits.

Renders commit metadata loaded from a spreadsheet or extracted directly from Git,
and passes it to the template for interactive browsing.
"""

import pandas as pd
from tornado.web import RequestHandler

from utils.git import extract_commits_from_git


class MainHandler(RequestHandler):
    """Serves the main page showing a table of commits loaded from the spreadsheet."""

    df: pd.DataFrame
    repo_path: str

    def initialize(self):
        """Inject the preloaded DataFrame of commit metadata into the handler."""
        self.df = self.application.settings.get("df")
        self.repo_path = self.application.settings.get("repo_path")

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
