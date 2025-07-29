import logging 
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import quote

import pandas as pd
from tornado.web import RequestHandler, HTTPError

from utils.git import extract_commits_from_git
from utils.issues import find_commits_referring_to_issue

logger = logging.getLogger(__name__)
# logger.addHandler(logging.NullHandler())  # safe default


def find_issue_file(slug: str, issues_dir: Path) -> Path | None:
    for subdir in ("open", "closed"):
        path = issues_dir / subdir / f"{slug}.md"
        if path.exists():
            return path
    return None


class IssueDetailHandler(RequestHandler):
    def get(self, slug):
        """
        Look for the issue in issues/open/ or issues/closed/
        Render issue.html with its content.
        """
        repo_path: Path = self.application.settings["repo_path"]
        issues_dir: Path = self.application.settings["issues_dir"]

        issue_paths = [
            repo_path / "issues/open" / f"{slug}.md",
            repo_path / "issues/closed" / f"{slug}.md",
        ]

        path = find_issue_file(slug, issues_dir)
        if path is None:
            raise HTTPError(404, f"Issue {slug} not found in open/ or closed/")

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
            df = commit_metadata_store.df
            matches = df[df["issue"] == slug]
            sha_list = matches["sha"].tolist()

        # Scan all commits and filter only those matching spreadsheet-linked SHAs
        scanned_commits = [
            SimpleNamespace(**row)
            for row in extract_commits_from_git(repo_path)
        ]

        linked_commits = [
            row for row in scanned_commits
            if row.sha in sha_list
        ]

        logger.debug("linked_commits: %s", sha_list)

        referring = find_commits_referring_to_issue(slug, scanned_commits)

        # Merge in any inferred rows not already included
        for row in referring:
            if row.sha not in {c.sha for c in linked_commits}:
                linked_commits.append(row)
        
        self.render(
            "issue.html",
            slug=slug,
            status=status,
            content=content,
            linked_commits=linked_commits,
        )


class IssueUpdateHandler(RequestHandler):
    def post(self, slug: str):
        issues_dir: Path = self.application.settings["issues_dir"]
        markdown = self.get_body_argument("markdown")

        path = find_issue_file(slug, issues_dir)
        if path is None:
            self.set_status(404)
            self.write("Issue not found.")
            return

        path.write_text(markdown, encoding="utf-8")
        self.redirect(f"/issue/{quote(slug)}")
