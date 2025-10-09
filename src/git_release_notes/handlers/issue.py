import logging
import os
from pathlib import Path
import re
from types import SimpleNamespace
from urllib.parse import quote

from tornado.web import RequestHandler, HTTPError

from ..utils.git import extract_commits_from_git
from ..utils.issues import find_commits_referring_to_issue

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

        path = find_issue_file(slug, issues_dir)
        if path is None:
            raise HTTPError(404, f"Issue {slug} not found in open/ or closed/")

        with path.open(encoding="utf-8") as f:
            content = f.read()
        status = path.parent.name

        commit_metadata_store = self.application.settings.get("commit_metadata_store")
        linked_commits = []

        # Refresh store (no-op for in-memory stores), then ask it for SHAs
        try:
            commit_metadata_store.reload()
        except Exception as e:
            logger.warning("Failed to reload commit metadata store: %s", e)
        sha_list = commit_metadata_store.shas_for_issue(slug)


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


_NEWLINE_RE = re.compile(r'\r\n|\r|\n')


def detect_dominant_eol(s: str) -> str | None:
    """Return '\r\n', '\n', or '\r' if s contains newlines; pick the dominant one.
    Return None if no newlines found."""
    crlf = s.count('\r\n')
    # Count lone CR and LF that aren't part of CRLF (simple but works well enough)
    # Replace CRLF temporarily to avoid double-count
    tmp = s.replace('\r\n', '\0')
    cr = tmp.count('\r')
    lf = tmp.count('\n')
    if crlf == cr == lf == 0:
        return None
    # Choose the most frequent; break ties preferring CRLF, then LF.
    counts = [('\r\n', crlf), ('\n', lf), ('\r', cr)]
    counts.sort(key=lambda x: x[1], reverse=True)
    return counts[0][0]


def normalize_to(s: str, target_eol: str) -> str:
    # First normalize everything to LF, then to target
    s_lf = _NEWLINE_RE.sub('\n', s)
    return s_lf.replace('\n', target_eol)


class IssueUpdateHandler(RequestHandler):
    def post(self, slug: str):
        issues_dir: Path = self.application.settings["issues_dir"]
        markdown = self.get_body_argument("markdown")

        path = find_issue_file(slug, issues_dir)
        if path is None:
            self.set_status(404)
            self.write("Issue not found.")
            return

        # 1) Detect target EOL from existing file (if any)
        target_eol = os.linesep  # platform-native default
        if path.exists():
            try:
                existing = path.read_text(encoding="utf-8", errors="ignore")
                eol = detect_dominant_eol(existing)
                if eol:
                    target_eol = eol
            except Exception:
                pass  # fall back to os.linesep

        # 2) Normalize incoming content to target EOL
        out = normalize_to(markdown, target_eol)

        # 3) Write exactly as-is (no newline translation!)
        #    newline='' disables universal newline conversion on write.
        path.write_text(out, encoding="utf-8", newline="")

        self.redirect(f"/issue/{quote(slug)}")
