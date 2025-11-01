"""
Request handler for the issue-centric browsing index.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable
from urllib.parse import urlencode

from tornado.web import RequestHandler

from ..utils.issue_index import IssueIndexRow, collect_issue_index_rows, group_releases
from ..utils.metadata_store import CommitMetadataStore


def _format_date(value: datetime | None, *, include_time: bool = False) -> str:
    if value is None:
        return ""
    value = value.astimezone(timezone.utc)
    return value.strftime("%Y-%m-%d %H:%M" if include_time else "%Y-%m-%d")


def _build_url(sort_mode: str, release: str | None) -> str:
    params: list[tuple[str, str]] = []
    if sort_mode:
        params.append(("sort", sort_mode))
    if release:
        params.append(("release", release))
    query = urlencode(params)
    return "/issues" if not query else f"/issues?{query}"


def _normalize_sort(value: str) -> str:
    value = (value or "").lower()
    if value not in {"updated", "landed"}:
        return "updated"
    return value


def _status_badge(status: str) -> str:
    return "bg-success" if status == "open" else "bg-secondary"


@dataclass(frozen=True, slots=True)
class IssueIndexViewRow:
    slug: str
    status: str
    status_badge: str
    release: str | None
    last_updated: str
    landed_at: str
    issue_url: str
    commit_index_url: str


def _sort_rows(rows: Iterable[IssueIndexRow], sort_mode: str) -> list[IssueIndexRow]:
    if sort_mode == "landed":
        return sorted(
            rows,
            key=lambda row: (row.landed_at or datetime.min.replace(tzinfo=timezone.utc), row.slug),
            reverse=True,
        )
    return sorted(
        rows,
        key=lambda row: (row.last_updated, row.slug),
        reverse=True,
    )


class IssueIndexHandler(RequestHandler):
    """Render the issue index page with release and landing metadata."""

    repo_path: str
    issues_dir: str
    store: CommitMetadataStore

    def initialize(self) -> None:
        self.repo_path = self.application.settings.get("repo_path")
        self.issues_dir = self.application.settings.get("issues_dir")
        self.store = self.application.settings.get("commit_metadata_store")

    def data_received(self, chunk):
        return None

    def get(self):
        sort_mode = _normalize_sort(self.get_query_argument("sort", "updated"))
        release_filter = self.get_query_argument("release", default=None)
        if release_filter:
            release_filter = release_filter.strip() or None

        all_rows = collect_issue_index_rows(self.repo_path, self.issues_dir, self.store)
        if release_filter:
            rows = [row for row in all_rows if row.release == release_filter]
        else:
            rows = list(all_rows)

        ordered_rows = _sort_rows(rows, sort_mode)

        view_rows = [
            IssueIndexViewRow(
                slug=row.slug,
                status=row.status,
                status_badge=_status_badge(row.status),
                release=row.release,
                last_updated=_format_date(row.last_updated),
                landed_at=_format_date(row.landed_at, include_time=True) if row.landed_at else "",
                issue_url=f"/issue/{row.slug}",
                commit_index_url=f"/?issue={row.slug}",
            )
            for row in ordered_rows
        ]

        releases = group_releases(all_rows)

        sort_options = [
            {
                "label": "Updated",
                "url": _build_url("updated", release_filter),
                "active": sort_mode == "updated",
            },
            {
                "label": "Landed",
                "url": _build_url("landed", release_filter),
                "active": sort_mode == "landed",
            },
        ]

        release_options = [
            {
                "label": "All Releases",
                "value": None,
                "url": _build_url(sort_mode, None),
                "active": release_filter is None,
            }
        ]
        for release in releases:
            release_options.append(
                {
                    "label": release,
                    "value": release,
                    "url": _build_url(sort_mode, release),
                    "active": release_filter == release,
                }
            )

        self.render(
            "issue-index.html",
            rows=view_rows,
            sort_options=sort_options,
            release_options=release_options,
            selected_sort=sort_mode,
            selected_release=release_filter,
        )
