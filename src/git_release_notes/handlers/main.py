"""
MainHandler: Serves the main page displaying a table of commits.

Renders commit metadata loaded from a spreadsheet or extracted directly from Git,
and passes it to the template for interactive browsing.
"""

import logging

from tornado.web import RequestHandler

from ..utils.git import extract_commits_from_git, run_git
from ..utils.issue_suggestions import compute_issue_suggestion
from ..utils.metadata_store import CommitMetadataStore

logger = logging.getLogger(__name__)


class MainHandler(RequestHandler):
    """Serves the main page showing a table of commits loaded from the spreadsheet."""

    repo_path: str
    store: CommitMetadataStore

    def initialize(self):
        """Inject the preloaded DataFrame of commit metadata into the handler."""
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

        metadata_df = self.store.get_metadata_df()

        if self.store.limits_commit_set():
            rows = metadata_df.to_dict(orient="records")
        else:
            git_rows = extract_commits_from_git(self.repo_path)

            logger.info("Extracted %d git commits", len(git_rows))
            for row in git_rows:
                logger.info("GIT SHA: %s — %s", row["sha"], row["message"])

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

        for row in rows:
            touched_paths = row.get("touched_paths")
            if touched_paths is None:
                touched_paths = self._get_touched_paths(row["sha"])

            suggestion = compute_issue_suggestion(
                self.repo_path,
                row.get("message", ""),
                touched_paths=touched_paths,
            )
            suggestion_value = suggestion.suggestion
            if suggestion_value and suggestion_value == (row.get("issue") or "").strip():
                suggestion_value = None
            row["issue_suggestion"] = suggestion_value
            row["issue_suggestion_source"] = suggestion.suggestion_source if suggestion_value else None

        self.render("index.html", rows=rows)

    def _get_touched_paths(self, sha: str) -> list[str]:
        """Retrieve touched paths for commits lacking precomputed file lists."""
        result = run_git(self.repo_path, "show", "--name-only", "--pretty=format:", sha, check=True)
        return [line.strip() for line in result.stdout.splitlines() if line.strip()]
