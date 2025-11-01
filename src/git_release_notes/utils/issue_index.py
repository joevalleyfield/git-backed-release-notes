"""
Utilities for building the issue-centric index view.

Collects issue files from the repository, enriches them with release and landing
metadata, and prepares rows suitable for rendering in the Tornado templates.
"""

from __future__ import annotations

import csv
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Sequence

from .git import run_git
from .metadata_store import CommitMetadataStore

logger = logging.getLogger(__name__)


def _parse_timestamp(value: str) -> datetime | None:
    """Parse a timestamp string into an aware datetime where possible."""
    if not value:
        return None

    text = value.strip()
    if not text:
        return None

    # Try ISO-8601 first (handles YYYY-MM-DD and YYYY-MM-DDTHH:MM:SS).
    try:
        dt = datetime.fromisoformat(text)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except ValueError:
        pass

    # Accept common fallback "YYYY-MM-DD HH:MM" pattern.
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(text, fmt).replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            continue

    logger.debug("Failed to parse timestamp '%s'", value)
    return None


def _extract_front_matter(path: Path) -> dict[str, str]:
    """
    Parse simple `key: value` pairs from the top portion of an issue Markdown file.

    Stops parsing once a blank line is encountered to avoid walking the full document.
    """
    data: dict[str, str] = {}
    try:
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    break
                if ":" not in line:
                    continue
                key, value = line.split(":", 1)
                data[key.strip().lower()] = value.strip()
    except FileNotFoundError:
        logger.debug("Issue file %s disappeared before parsing front matter", path)
    return data


def _git_last_updated(repo_root: Path, issue_path: Path) -> datetime | None:
    """Lookup the last commit timestamp that touched the given issue file."""
    rel_path = issue_path.relative_to(repo_root)
    try:
        result = run_git(repo_root, "log", "-1", "--format=%cI", str(rel_path), check=True)
    except Exception as exc:  # broad: git may not know about the file yet
        logger.debug("git log failed for %s: %s", rel_path, exc)
        return None

    timestamp = result.stdout.strip()
    return _parse_timestamp(timestamp)


def _fs_last_modified(issue_path: Path) -> datetime:
    """Fallback to the filesystem modification time when Git history is absent."""
    mtime = issue_path.stat().st_mtime
    return datetime.fromtimestamp(mtime, tz=timezone.utc)


def _collect_issue_files(issues_root: Path) -> Sequence[Path]:
    """Return all issue Markdown files from open/ and closed/ directories."""
    files: list[Path] = []
    if not issues_root.exists():
        return files

    for status_subdir in ("open", "closed"):
        directory = issues_root / status_subdir
        if not directory.exists():
            continue
        for path in sorted(directory.glob("*.md")):
            files.append(path)
    return files


def _load_release_map(metadata_df) -> dict[str, str]:
    """Build a mapping of issue slug to its associated release (first non-empty)."""
    release_map: dict[str, str] = {}
    if metadata_df is None or metadata_df.empty:
        return release_map

    for _, row in metadata_df.iterrows():
        issue_slug = str(row.get("issue", "")).strip()
        if not issue_slug:
            continue
        release = str(row.get("release", "")).strip()
        if not release:
            continue
        release_map.setdefault(issue_slug, release)
    return release_map


def _load_commit_landings(repo_root: Path) -> tuple[dict[str, datetime], dict[str, list[str]]]:
    """
    Read commits.csv, returning landing timestamps per issue and shas grouped by issue.
    """
    path = repo_root / "commits.csv"
    landing_map: dict[str, datetime] = {}
    sha_map: dict[str, list[str]] = {}

    if not path.exists():
        return landing_map, sha_map

    try:
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                issue_slug = (row.get("issue") or "").strip()
                if not issue_slug:
                    continue
                sha = (row.get("sha") or "").strip()
                if sha:
                    sha_map.setdefault(issue_slug, []).append(sha)
                landed_at = _parse_timestamp(row.get("landed_at", ""))
                if landed_at is None:
                    continue
                existing = landing_map.get(issue_slug)
                if existing is None or landed_at > existing:
                    landing_map[issue_slug] = landed_at
    except Exception as exc:  # pragma: no cover - defensive path
        logger.warning("Failed to read commits.csv for issue index: %s", exc)

    return landing_map, sha_map


@dataclass(frozen=True, slots=True)
class IssueIndexRow:
    slug: str
    status: str
    release: str | None
    last_updated: datetime
    landed_at: datetime | None
    commit_shas: tuple[str, ...]


def collect_issue_index_rows(
    repo_root: Path,
    issues_root: Path,
    store: CommitMetadataStore,
) -> list[IssueIndexRow]:
    """
    Gather issue metadata enriched with release and landing timestamps.
    """
    store.reload()
    metadata_df = store.get_metadata_df()
    release_map = _load_release_map(metadata_df)
    landing_map, commit_sha_map = _load_commit_landings(repo_root)

    rows: list[IssueIndexRow] = []
    for path in _collect_issue_files(issues_root):
        status = path.parent.name  # open / closed
        slug = path.stem

        front_matter = _extract_front_matter(path)

        release = front_matter.get("release") or release_map.get(slug) or ""
        release_val = release if release else None

        last_updated = _parse_timestamp(front_matter.get("last_updated", "")) or _git_last_updated(
            repo_root, path
        )
        if last_updated is None:
            last_updated = _fs_last_modified(path)

        landed_at = landing_map.get(slug)

        commit_shas = set(commit_sha_map.get(slug, []))

        # Also include shas from metadata store in case commits.csv lacks entries.
        if metadata_df is not None and not metadata_df.empty:
            matches = metadata_df[metadata_df["issue"] == slug]
            commit_shas.update(str(sha).strip() for sha in matches["sha"] if str(sha).strip())

        rows.append(
            IssueIndexRow(
                slug=slug,
                status=status,
                release=release_val,
                last_updated=last_updated,
                landed_at=landed_at,
                commit_shas=tuple(sorted(commit_shas)),
            )
        )

    return rows


def group_releases(rows: Iterable[IssueIndexRow]) -> list[str]:
    """Return a sorted list of unique release names from the issue index rows."""
    releases = {row.release for row in rows if row.release}
    return sorted(releases)
