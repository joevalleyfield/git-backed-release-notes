"""
MainHandler: Serves the main page displaying a table of commits.

Renders commit metadata loaded from a spreadsheet or extracted directly from Git,
and passes it to the template for interactive browsing.
"""

import logging
import math

from tornado.web import RequestHandler

from ..utils.git import extract_commits_from_git, run_git
from ..utils.issue_suggestions import compute_issue_suggestion
from ..utils.metadata_store import CommitMetadataStore
from ..utils.release_suggestions import compute_release_suggestion

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

        tag_pattern = self.application.settings.get("tag_pattern", "rel-*")

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

            raw_release = row.get("release", "")
            if isinstance(raw_release, str):
                release_value = raw_release.strip()
            elif raw_release is None:
                release_value = ""
            elif isinstance(raw_release, float):
                release_value = "" if math.isnan(raw_release) else str(raw_release)
            else:
                release_value = str(raw_release)
            row["release"] = release_value

            release_suggestion = compute_release_suggestion(
                self.repo_path,
                row["sha"],
                current_release=release_value,
                tag_pattern=tag_pattern,
            )
            if release_suggestion.suggestion:
                row["release_suggestion"] = release_suggestion.suggestion
                source = release_suggestion.suggestion_source
                row["release_suggestion_source"] = source
                row["release_suggestion_label"] = source.title() if source else None
            else:
                row["release_suggestion"] = None
                row["release_suggestion_source"] = None
                row["release_suggestion_label"] = None

        self.render("index.html", rows=rows)

    def _get_touched_paths(self, sha: str) -> list[str]:
        """Retrieve touched paths for commits lacking precomputed file lists."""
        result = run_git(self.repo_path, "show", "--name-only", "--pretty=format:", sha, check=True)
        return [line.strip() for line in result.stdout.splitlines() if line.strip()]
