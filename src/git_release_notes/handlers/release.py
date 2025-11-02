"""
Handlers supporting release-centric browsing and detail views.

These views aggregate commit metadata from the shared store and enrich it with
issue note information and Git commit details so that releases can be explored
without leaving the app.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from tornado.web import HTTPError, RequestHandler

from ..utils.git import (
    find_follows_tag,
    find_precedes_tag,
    get_matching_tag_commits,
    run_git,
)
from .issue import find_issue_file

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class ReleaseCommit:
    sha: str
    short_sha: str
    subject: str
    author_date: str
    issue: str


@dataclass(frozen=True, slots=True)
class ReleaseIssue:
    slug: str
    status: str | None
    title: str | None
    path: Path | None


def _format_count(label: str, count: int) -> str:
    suffix = "s" if count != 1 else ""
    return f"{count} {label}{suffix}"


def _build_summary(issue_entries: list[ReleaseIssue], commits: list[ReleaseCommit]) -> dict:
    issue_count = len(issue_entries)
    commit_count = len(commits)
    latest_commit = commits[0].author_date if commits else None
    earliest_commit = commits[-1].author_date if commits else None

    return {
        "issue_count": issue_count,
        "commit_count": commit_count,
        "latest_commit": latest_commit,
        "earliest_commit": earliest_commit,
        "text": f"{_format_count('issue', issue_count)} • {_format_count('commit', commit_count)}",
    }


def _resolve_tag_metadata(
    repo_path: Path,
    commits: list[ReleaseCommit],
    tag_pattern: str,
) -> dict | None:
    if not commits:
        return None

    repo = str(repo_path)
    sha = commits[0].sha
    short_sha = commits[0].short_sha

    tag_map = get_matching_tag_commits(repo, tag_pattern)
    direct_tag = tag_map.get(sha)
    if direct_tag:
        return {
            "direct": True,
            "tag": direct_tag,
            "short_sha": short_sha,
            "previous": None,
            "previous_count": None,
            "next": None,
        }

    previous = find_follows_tag(sha, repo, tag_pattern)
    next_tag = find_precedes_tag(sha, repo, tag_pattern)

    if previous is None and next_tag is None:
        return None

    return {
        "direct": False,
        "tag": None,
        "short_sha": short_sha,
        "previous": previous.base_tag if previous else None,
        "previous_count": getattr(previous, "count", None) if previous else None,
        "next": next_tag.base_tag if next_tag else None,
    }


def _extract_heading(markdown: str) -> str | None:
    """Return the first Markdown heading, if present."""
    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip()
    return None


def _load_issue_entry(slug: str, issues_dir: Path) -> ReleaseIssue:
    path = find_issue_file(slug, issues_dir)
    if path is None:
        return ReleaseIssue(slug=slug, status=None, title=None, path=None)

    try:
        contents = path.read_text(encoding="utf-8")
    except OSError as exc:
        logger.warning("Failed to read issue note for %s: %s", slug, exc)
        return ReleaseIssue(slug=slug, status=path.parent.name, title=None, path=path)

    title = _extract_heading(contents)
    return ReleaseIssue(slug=slug, status=path.parent.name, title=title, path=path)


def _load_commit_entry(repo_path: Path, sha: str, issue: str) -> ReleaseCommit | None:
    try:
        cp = run_git(
            repo_path,
            "show",
            "-s",
            "--format=%H%n%h%n%ad%n%s",
            "--date=iso",
            sha,
            check=True,
        )
    except Exception as exc:  # broad to ensure UX isn’t blocked by git anomalies
        logger.warning("Failed to load commit %s for release view: %s", sha, exc)
        return None

    lines = [line.strip() for line in cp.stdout.splitlines() if line.strip()]
    if len(lines) < 4:
        logger.warning("Unexpected git output for %s: %r", sha, cp.stdout)
        return None

    full_sha, short_sha, author_date, subject = lines[:4]
    return ReleaseCommit(
        sha=full_sha,
        short_sha=short_sha,
        author_date=author_date,
        subject=subject,
        issue=issue,
    )


def _collect_release_groups(records: Iterable[dict]) -> dict[str, dict]:
    releases: dict[str, dict] = {}
    for record in records:
        release = str(record.get("release") or "").strip()
        if not release:
            continue
        sha = str(record.get("sha") or "").strip()
        issue = str(record.get("issue") or "").strip()

        bucket = releases.setdefault(
            release,
            {
                "slug": release,
                "commits": {},
                "issues": set(),
            },
        )

        if sha:
            bucket["commits"][sha] = {"sha": sha, "issue": issue}
        if issue:
            bucket["issues"].add(issue)
    return releases


class ReleaseIndexHandler(RequestHandler):
    """Render a list of releases with high-level counts."""

    def get(self):
        store = self.application.settings.get("commit_metadata_store")
        issues_dir: Path = self.application.settings.get("issues_dir")

        try:
            store.reload()
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("Failed to reload commit metadata store: %s", exc)

        df = store.get_metadata_df()
        records = df.to_dict(orient="records") if not df.empty else []

        releases = _collect_release_groups(records)

        release_rows = []
        for release_slug, bucket in sorted(releases.items()):
            issue_entries = [
                _load_issue_entry(slug, issues_dir)
                for slug in sorted(bucket["issues"])
            ]
            release_rows.append(
                {
                    "slug": release_slug,
                    "issue_count": sum(1 for entry in issue_entries if entry.slug),
                    "commit_count": len(bucket["commits"]),
                }
            )

        self.render(
            "release-index.html",
            releases=release_rows,
        )


class ReleaseDetailHandler(RequestHandler):
    """Render an individual release with its commits and linked issues."""

    def get(self, release_slug: str):
        store = self.application.settings.get("commit_metadata_store")
        repo_path: Path = self.application.settings.get("repo_path")
        issues_dir: Path = self.application.settings.get("issues_dir")
        tag_pattern: str = self.application.settings.get("tag_pattern", "rel-*")

        try:
            store.reload()
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("Failed to reload commit metadata store: %s", exc)

        df = store.get_metadata_df()
        records = df.to_dict(orient="records") if not df.empty else []

        releases = _collect_release_groups(records)
        if release_slug not in releases:
            raise HTTPError(404, f"Release {release_slug} not found")

        bucket = releases[release_slug]

        issue_entries = []
        for slug in sorted(bucket["issues"]):
            entry = _load_issue_entry(slug, issues_dir)
            issue_entries.append(entry)

        commits: list[ReleaseCommit] = []
        for sha, info in bucket["commits"].items():
            commit_entry = _load_commit_entry(repo_path, sha, info.get("issue", ""))
            if commit_entry:
                commits.append(commit_entry)

        commits.sort(key=lambda commit: commit.author_date, reverse=True)

        summary = _build_summary(issue_entries, commits)
        tag_metadata = _resolve_tag_metadata(repo_path, commits, tag_pattern)

        self.render(
            "release-detail.html",
            release={"slug": release_slug},
            issues=issue_entries,
            commits=commits,
            summary=summary,
            tag_metadata=tag_metadata,
        )
