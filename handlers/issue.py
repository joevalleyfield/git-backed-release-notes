import logging 
from pathlib import Path

from tornado.web import RequestHandler, HTTPError

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())  # safe default

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
                    # This assumes a DataFrame-based store — safe for no-xlsx mode
                    df = commit_metadata_store.df
                    matches = df[df["issue"] == slug]
                    linked_commits = matches["sha"].tolist()

                self.render("issue.html", slug=slug, status=status, content=content, linked_commits=linked_commits)
                return

        raise HTTPError(404, f"Issue {slug} not found in open/ or closed/")

class UpdateIssueHandler(RequestHandler):
    def post(self, slug):
        body = self.get_argument("markdown", None)
        if body is None:
            raise HTTPError(400, "Missing markdown content")

        repo_path = self.settings.get("repo_path")
        issue_path = repo_path / "issues/open" / f"{slug}.md"
        if not issue_path.exists():
            raise HTTPError(404, f"Issue file not found: {issue_path}")

        logger.debug(
            "Writing issue to: issue_path=%s body=%s", issue_path, body
        )

        issue_path.write_text(body, encoding="utf-8")
        self.redirect(f"/issue/{slug}")