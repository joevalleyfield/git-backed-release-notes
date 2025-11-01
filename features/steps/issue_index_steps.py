"""Step definitions for issue_index.feature."""

from __future__ import annotations

import csv
from datetime import datetime, timezone
from typing import Iterable

import requests
from behave import given, then, when  # pylint: disable=no-name-in-module
from bs4 import BeautifulSoup
from features.support.git_helpers import create_timestamped_commit_touching_issue

from tests.helpers.issue_index_fixtures import (
    ISSUE_INDEX_FIXTURE,
    IssueRecord,
    ensure_issue_files,
    write_commits_csv,
    write_metadata_csv,
)


def _parse_issue_records(table) -> list[IssueRecord]:
    records: list[IssueRecord] = []
    for row in table:
        last_updated = datetime.strptime(row["last_updated"], "%Y-%m-%d").replace(tzinfo=timezone.utc)
        records.append(
            IssueRecord(
                slug=row["slug"],
                status=row["status"],
                release=row["release"],
                last_updated=last_updated,
            )
        )
    return records


def _parse_landing_map(table) -> dict[str, datetime]:
    landing: dict[str, datetime] = {}
    for row in table:
        landed_at = datetime.strptime(row["landed_at"], "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
        landing[row["slug"]] = landed_at
    return landing


def _record_release_map(records: Iterable[IssueRecord]) -> dict[str, str]:
    return {record.slug: record.release for record in records}


@given("the issues directory contains issue metadata for:")
def step_populate_issue_metadata(context):
    table = context.table
    records = _parse_issue_records(table)
    context.issue_index_records = records

    ensure_issue_files(context.repo_path, records)


@given("commit landing data exists for issues:")
def step_populate_commit_fixtures(context):
    table = context.table
    landing_map = _parse_landing_map(table)
    context.issue_landing_map = landing_map

    records = getattr(context, "issue_index_records", ISSUE_INDEX_FIXTURE)
    release_map = _record_release_map(records)

    # Create deterministic synthetic commit ids aligned with issue slugs.
    commit_ids = {slug: f"fixture-{idx:02d}" for idx, slug in enumerate(landing_map.keys(), start=1)}
    context.issue_commit_map = commit_ids

    write_metadata_csv(
        context.repo_path,
        commit_issue_map={sha: slug for slug, sha in commit_ids.items()},
        releases=release_map,
    )
    write_commits_csv(
        context.repo_path,
        landing_map,
        commit_ids=commit_ids,
    )


@given('landing data is cleared for issue "{slug}"')
def step_clear_landing_data(context, slug):
    path = context.repo_path / "commits.csv"
    if not path.exists():
        return

    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = [row for row in reader if row.get("issue") != slug]

    if not rows:
        path.write_text("sha,summary,issue,landed_at\n", encoding="utf-8")
        return

    fieldnames = ["sha", "summary", "issue", "landed_at"]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


@given('metadata links are cleared for issue "{slug}"')
def step_clear_metadata_links(context, slug):
    path = context.repo_path / "git-view.metadata.csv"
    if not path.exists():
        return

    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        if not rows:
            return

    fieldnames = reader.fieldnames or ["sha", "issue", "release"]
    for row in rows:
        if row.get("issue") == slug:
            row["issue"] = ""

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


@given('a commit touching issue "{slug}" landed at "{iso_timestamp}"')
def step_create_timestamped_commit(context, slug, iso_timestamp):
    create_timestamped_commit_touching_issue(
        context.repo_path,
        slug,
        f"Touch {slug}",
        iso_timestamp,
    )


def _ensure_params(context):
    if not hasattr(context, "issue_index_params"):
        context.issue_index_params = {}


def _fetch_issue_index(context):
    base_url = f"{context.server.base_url}/issues"
    params = getattr(context, "issue_index_params", {})
    response = requests.get(base_url, params=params, timeout=10)
    assert response.status_code == 200, f"Unexpected status {response.status_code}: {response.text}"
    context.issue_index_response = response
    context.issue_index_soup = BeautifulSoup(response.text, "html.parser")


@when("the user visits the issue index")
def step_visit_issue_index(context):
    _ensure_params(context)
    _fetch_issue_index(context)


@when('selects the "{sort_label}" sort')
def step_select_sort(context, sort_label):
    _ensure_params(context)
    sort_slug = {"Updated": "updated", "Landed": "landed"}.get(sort_label)
    assert sort_slug, f"Unknown sort label '{sort_label}'"
    context.issue_index_params["sort"] = sort_slug
    _fetch_issue_index(context)


@when('filters issues by release "{release_slug}"')
def step_filter_by_release(context, release_slug):
    _ensure_params(context)
    context.issue_index_params["release"] = release_slug
    _fetch_issue_index(context)


def _current_issue_rows(context):
    soup: BeautifulSoup = context.issue_index_soup
    rows = soup.select("tr[data-test='issue-row']")
    assert rows, "No issue rows rendered"
    return rows


@then("the issue list should order slugs as:")
def step_assert_issue_order(context):
    table = context.table
    rows = _current_issue_rows(context)
    expected_order = [row["slug"] for row in sorted(table, key=lambda r: int(r["position"]))]
    actual_subset = [row.get("data-slug") for row in rows if row.get("data-slug") in expected_order]
    assert (
        actual_subset == expected_order
    ), f"Expected slug order {expected_order}, saw {actual_subset} within rendered rows"


@then("the issue list should show slugs:")
def step_assert_issue_subset(context):
    table = context.table
    rows = _current_issue_rows(context)
    actual = [
        (
            row.get("data-slug"),
            row.select_one("[data-test='issue-status']").get_text(strip=True),
        )
        for row in rows
    ]
    expected = [(entry["slug"], entry["status"]) for entry in table]
    assert actual == expected, f"Expected rows {expected}, saw {actual}"


@then("the header should link to the commit index")
def step_assert_header_commit_link(context):
    soup: BeautifulSoup = context.issue_index_soup
    link = soup.select_one("a[data-test='issues-commit-index-link']")
    assert link is not None, "Expected header commit index link"
    href = link.get("href", "")
    assert href == "/", f"Expected commit index link to '/', saw '{href}'"


@then("issue rows should not include commit navigation links")
def step_assert_issue_rows_no_commit_links(context):
    rows = _current_issue_rows(context)
    for row in rows:
        slug = row.get("data-slug")
        link = row.select_one("a[data-test='issue-commit-link']")
        assert link is None, f"Did not expect commit navigation link in row for {slug}"


@then('issue "{slug}" should show last landed "{expected}"')
def step_assert_last_landed(context, slug, expected):
    rows = _current_issue_rows(context)
    for row in rows:
        if row.get("data-slug") == slug:
            cell = row.select_one("[data-test='issue-landed-at']")
            assert cell is not None, f"No landed-at cell found for issue {slug}"
            text = cell.get_text(strip=True)
            assert (
                text == expected
            ), f"Expected issue {slug} to show '{expected}' in Last Landed, saw '{text}'"
            return
    raise AssertionError(f"Issue row for {slug} not found in rendered issue index")
