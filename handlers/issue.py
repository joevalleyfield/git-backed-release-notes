import logging 
from pathlib import Path

import pandas as pd
from tornado.web import RequestHandler, HTTPError

logger = logging.getLogger(__name__)
# logger.addHandler(logging.NullHandler())  # safe default

class IssueDetailHandler(RequestHandler):
    def get(self, slug):
        """
        Look for the issue in issues/open/ or issues/closed/
        Render issue.html with its content.
        """
        repo_path = self.application.settings.get("repo_path")
        issue_paths = [
            repo_path / "issues/open" / f"{slug}.md",
            repo_path / "issues/closed" / f"{slug}.md",
        ]

        for path in issue_paths:
            if path.exists():
                with path.open(encoding="utf-8") as f:
                    content = f.read()
                status = path.parent.name

                commit_metadata_store = self.application.settings.get("commit_metadata_store")
                linked_commits = []

                if hasattr(commit_metadata_store, "df"):
                    try:
                        commit_metadata_store.df = pd.read_csv(commit_metadata_store.path)
                    except Exception as e:
                        logger.warning("Failed to reload commit metadata store: %s", e)
                    # This assumes a DataFrame-based store — safe for no-xlsx mode
                    df = commit_metadata_store.df
                    matches = df[df["issue"] == slug]
                    linked_commits = matches["sha"].tolist()

                logger.debug("linked_commits: %s", linked_commits)

                self.render("issue.html", slug=slug, status=status, content=content, linked_commits=linked_commits)
                return

        raise HTTPError(404, f"Issue {slug} not found in open/ or closed/")

