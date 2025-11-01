"""
Shared fixture data and helpers for the issue-centric browsing feature.

The goal of these utilities is to keep Behave scenarios and unit tests aligned
on a single set of canonical issue records, including release and landing
metadata. Tests can import the constants defined here to seed filesystem data
or to reason about ordering expectations without repeating literal strings.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Mapping


@dataclass(frozen=True, slots=True)
class IssueRecord:
    """Represents a single issue row for the index fixture."""

    slug: str
    status: str
    release: str
    last_updated: datetime

    def last_updated_iso(self) -> str:
        """Return the last-updated timestamp in ISO format."""
        return self.last_updated.astimezone(timezone.utc).date().isoformat()


ISSUE_INDEX_FIXTURE: tuple[IssueRecord, ...] = (
    IssueRecord(
        slug="open-ux-tweaks",
        status="open",
        release="release-a",
        last_updated=datetime(2024, 2, 14, tzinfo=timezone.utc),
    ),
    IssueRecord(
        slug="closed-fix-off-by-one",
        status="closed",
        release="release-a",
        last_updated=datetime(2024, 2, 11, tzinfo=timezone.utc),
    ),
    IssueRecord(
        slug="closed-add-breadcrumbs",
        status="closed",
        release="release-b",
        last_updated=datetime(2024, 1, 29, tzinfo=timezone.utc),
    ),
    IssueRecord(
        slug="open-add-merge-guard",
        status="open",
        release="release-b",
        last_updated=datetime(2024, 1, 26, tzinfo=timezone.utc),
    ),
)


IssueLandingMap = Mapping[str, datetime]

ISSUE_LANDING_FIXTURE: IssueLandingMap = {
    "open-ux-tweaks": datetime(2024, 2, 13, 10, 0, tzinfo=timezone.utc),
    "closed-fix-off-by-one": datetime(2024, 2, 10, 8, 15, tzinfo=timezone.utc),
    "closed-add-breadcrumbs": datetime(2024, 1, 31, 16, 45, tzinfo=timezone.utc),
    "open-add-merge-guard": datetime(2024, 2, 1, 9, 30, tzinfo=timezone.utc),
}


def ensure_issue_files(repo_root: Path, issues: Iterable[IssueRecord] = ISSUE_INDEX_FIXTURE) -> list[Path]:
    """
    Materialize Markdown skeletons for the provided issues beneath the repo root.

    Returns the list of file paths that were written. Files are overwritten if they
    already exist so tests can call this repeatedly to reset state.
    """
    paths: list[Path] = []
    for record in issues:
        base_dir = repo_root / "issues" / record.status
        base_dir.mkdir(parents=True, exist_ok=True)
        path = base_dir / f"{record.slug}.md"
        contents = [
            f"# {record.slug.replace('-', ' ').title()}",
            f"status: {record.status}",
            f"release: {record.release}",
            f"last_updated: {record.last_updated_iso()}",
            "",
        ]
        path.write_text("\n".join(contents), encoding="utf-8")
        paths.append(path)
    return paths


def write_metadata_csv(
    repo_root: Path,
    commit_issue_map: Mapping[str, str],
    *,
    releases: Mapping[str, str] | None = None,
) -> Path:
    """
    Emit a `git-view.metadata.csv` file that aligns commits to issues/releases.

    Args:
        repo_root: Base repository fixture directory.
        commit_issue_map: Mapping from commit SHA (or label) to issue slug.
        releases: Optional mapping from issue slug to release slug. If omitted,
                  releases from ISSUE_INDEX_FIXTURE will be used.
    """
    release_lookup = {record.slug: record.release for record in ISSUE_INDEX_FIXTURE}
    if releases:
        release_lookup.update(releases)

    metadata_path = repo_root / "git-view.metadata.csv"
    lines = ["sha,issue,release"]
    for sha, issue_slug in commit_issue_map.items():
        release = release_lookup.get(issue_slug, "")
        lines.append(f"{sha},{issue_slug},{release}")

    metadata_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return metadata_path


def write_commits_csv(
    repo_root: Path,
    landing_map: IssueLandingMap = ISSUE_LANDING_FIXTURE,
    *,
    commit_ids: Mapping[str, str] | None = None,
) -> Path:
    """
    Produce a lightweight commits CSV with landed-at timestamps keyed by issue slug.

    Args:
        repo_root: Base repository fixture directory.
        landing_map: Mapping of issue slug to landing datetime (UTC assumed).
        commit_ids: Optional mapping of issue slug to the commit identifier that
                    should be written. If omitted, synthetic fixture IDs are used.
    """
    commit_path = repo_root / "commits.csv"
    lines = ["sha,summary,issue,landed_at"]
    for idx, (issue_slug, landed_at) in enumerate(landing_map.items(), start=1):
        sha = commit_ids[issue_slug] if commit_ids and issue_slug in commit_ids else f"fixture-{idx:02d}"
        summary = issue_slug.replace("-", " ").title()
        landed_iso = landed_at.astimezone(timezone.utc).isoformat()
        lines.append(f"{sha},{summary},{issue_slug},{landed_iso}")

    commit_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return commit_path
