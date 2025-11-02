"""Step definitions for release_notes.feature."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict

import requests
from behave import given, then, when  # pylint: disable=no-name-in-module
from bs4 import BeautifulSoup
from hamcrest import assert_that, contains_string, equal_to, is_not, none

from tests.helpers.issue_index_fixtures import IssueRecord, ensure_issue_files, write_metadata_csv


@given("release issues exist:")
def step_release_issues_exist(context):
    records = []
    for row in context.table:
        records.append(
            IssueRecord(
                slug=row["slug"],
                status=row["status"],
                release=row["release"],
                last_updated=datetime.now(timezone.utc),
            )
        )

    ensure_issue_files(context.repo_path, records)
    context.release_issue_records = records


@given("release metadata assigns commits to releases:")
def step_release_metadata_assignments(context):
    commit_issue_map: Dict[str, str] = {}
    releases: Dict[str, str] = {}

    for row in context.table:
        label = row["commit_label"]
        issue = row["issue"]
        release = row["release"]
        sha = context.fixture_repo.sha_map.get(label)

        assert sha, f"Unknown commit label '{label}'"
        commit_issue_map[sha] = issue
        releases[issue] = release

    write_metadata_csv(context.repo_path, commit_issue_map, releases=releases)
    context.release_commit_map = commit_issue_map


@when("the user visits the release index")
def step_visit_release_index(context):
    url = f"{context.server.base_url}/releases"
    response = requests.get(url, timeout=10)
    assert response.status_code == 200, f"Unexpected status {response.status_code} for {url}"
    context.release_index_response = response
    context.release_index_soup = BeautifulSoup(response.text, "html.parser")


@then("the release list should show:")
def step_assert_release_list(context):
    soup: BeautifulSoup = context.release_index_soup
    rows = soup.select("[data-test='release-row']")
    assert rows, "Expected at least one release row in the index"

    actual = {}
    for row in rows:
        release_slug = row.get("data-release")
        commit_count_el = row.select_one("[data-test='release-commit-count']")
        issue_count_el = row.select_one("[data-test='release-issue-count']")
        assert release_slug, "Release row missing data-release attribute"
        assert commit_count_el is not None, f"Release row {release_slug} missing commit count"
        assert issue_count_el is not None, f"Release row {release_slug} missing issue count"
        actual[release_slug] = {
            "commit_count": commit_count_el.get_text(strip=True),
            "issue_count": issue_count_el.get_text(strip=True),
            "link": row.find("a", attrs={"data-test": "release-link"}),
        }

    for expected_row in context.table:
        release = expected_row["release"]
        assert release in actual, f"Expected release '{release}' in index, saw {list(actual)}"
        assert_that(actual[release]["issue_count"], equal_to(expected_row["issue_count"]))
        assert_that(actual[release]["commit_count"], equal_to(expected_row["commit_count"]))
        link_el = actual[release]["link"]
        assert_that(link_el, is_not(none()), f"Expected a detail link for release {release}")
        assert_that(link_el.get("href"), equal_to(f"/release/{release}"))


@when('the user visits the release detail for "{release_slug}"')
def step_visit_release_detail(context, release_slug):
    url = f"{context.server.base_url}/release/{release_slug}"
    response = requests.get(url, timeout=10)
    context.release_detail_response = response
    context.release_detail_soup = BeautifulSoup(response.text, "html.parser")


@then("the release detail should list issues:")
def step_assert_release_detail_issues(context):
    response = context.release_detail_response
    assert response.status_code == 200, f"Unexpected status {response.status_code}: {response.text}"

    soup: BeautifulSoup = context.release_detail_soup
    rows = soup.select("[data-test='release-issue']")
    assert rows, "Expected issue rows in the release detail view"

    actual = {
        row.get("data-slug"): row.select_one("[data-test='release-issue-status']").get_text(strip=True)
        for row in rows
    }

    for expected_row in context.table:
        slug = expected_row["issue_slug"]
        assert slug in actual, f"Issue '{slug}' not listed in release detail"
        assert_that(actual[slug], equal_to(expected_row["status"]))


@then("the release detail should list commits:")
def step_assert_release_detail_commits(context):
    soup: BeautifulSoup = context.release_detail_soup
    rows = soup.select("[data-test='release-commit']")
    assert rows, "Expected commit entries in the release detail view"

    rendered_truncated = {row.get("data-sha"): row for row in rows if row.get("data-sha")}

    for expected_row in context.table:
        label = expected_row["commit_label"]
        sha = context.fixture_repo.sha_map.get(label)
        assert sha, f"Unknown commit label '{label}'"
        truncated = sha[:7]
        assert truncated in rendered_truncated, f"Commit {label} ({truncated}) not listed in release detail"


@then('the release detail should include issue note heading "{heading}"')
def step_assert_release_detail_note_heading(context, heading):
    response = context.release_detail_response
    assert response.status_code == 200, f"Unexpected status {response.status_code}: {response.text}"
    assert_that(response.text, contains_string(heading))


@then('the release detail should show summary "{summary_text}"')
def step_assert_release_summary(context, summary_text):
    soup: BeautifulSoup = context.release_detail_soup
    summary = soup.select_one("[data-test='release-summary']")
    assert summary is not None, "Expected a release summary element"
    actual = summary.get_text(strip=True)
    assert_that(actual, equal_to(summary_text))


@then("release issues should link to their detail pages")
def step_assert_release_issue_links(context):
    soup: BeautifulSoup = context.release_detail_soup
    rows = soup.select("[data-test='release-issue']")
    assert rows, "Expected issues to be listed in the release detail"
    for row in rows:
        slug = row.get("data-slug")
        link = row.select_one("a[data-test='release-issue-link']")
        assert link is not None, f"Expected an issue link for {slug}"
        href = link.get("href", "")
        assert href == f"/issue/{slug}", f"Expected issue link href '/issue/{slug}', saw '{href}'"


@then("release commits should link to their detail pages")
def step_assert_release_commit_links(context):
    soup: BeautifulSoup = context.release_detail_soup
    rows = soup.select("[data-test='release-commit']")
    assert rows, "Expected commits to be listed in the release detail"
    for row in rows:
        short_sha = row.get("data-sha")
        link = row.select_one("a[data-test='release-commit-link']")
        assert link is not None, f"Expected a commit link for {short_sha}"
        href = link.get("href", "")
        assert_that(href, contains_string("/commit/"))


@then("the release detail should surface tag metadata")
def step_assert_release_tag_metadata(context):
    soup: BeautifulSoup = context.release_detail_soup
    element = soup.select_one("[data-test='release-tag-metadata']")
    assert element is not None, "Expected tag metadata to be displayed"
    text = element.get_text(strip=True)
    assert text, "Tag metadata element should not be empty"
    assert "rel-0.1" in text, f"Expected tag metadata to mention rel-0.1, saw '{text}'"
