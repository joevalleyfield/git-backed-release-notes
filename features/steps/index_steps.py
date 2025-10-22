"""Steps for index.feature."""

import requests
from behave import given, then, when  # pylint: disable=no-name-in-module
from bs4 import BeautifulSoup
from hamcrest import assert_that, equal_to, is_not, none

# pylint: disable=missing-function-docstring


@given("the server is running")
def step_server_running(context):
    assert_that(context.server, is_not(none()))


@given("the server is running without a spreadsheet")
def step_assert_no_spreadsheet_mode(context):
    assert_that(context.server.mode, matcher=equal_to("no_xlsx"))


@given("the server is running in file-backed mode")
def step_assert_file_backed_mode(context):
    assert_that(context.server.mode, matcher=equal_to("no_xlsx"))


@when("I visit the commit index")
@when("I GET the root page")
def step_get_root(context):
    context.response = requests.get(f"{context.server.base_url}/", timeout=5)


@then('the response should contain "{text}"')
def step_response_contains(context, text):
    assert context.response.status_code == 200
    assert text in context.response.text


@then('the response should contain the issue slug "{slug}"')
def step_response_contains_issue_slug(context, slug):
    assert context.response.status_code == 200
    assert slug in context.response.text, f"Issue slug '{slug}' not found in response {context.response.text}"


@then('the response should contain an anchor id for commit "{commit_label}"')
def step_anchor_id_for_commit(context, commit_label):
    sha = context.fixture_repo.shas[1] if commit_label == "middle" else None
    assert sha, f"No known SHA for label '{commit_label}'"
    soup = BeautifulSoup(context.response.text, "html.parser")
    el = soup.find(id=f"sha-{sha[:7]}")
    assert_that(el, is_not(none()), f"No element with id='sha-{sha[:7]}'")


def _find_row_for_current_commit(context):
    assert context.response.status_code == 200, "Expected a successful index response before querying rows"
    soup = BeautifulSoup(context.response.text, "html.parser")
    commit_sha = getattr(context, "commit_sha", None)
    assert commit_sha, "context.commit_sha was not set"
    row = soup.find("tr", id=f"sha-{commit_sha[:7]}")
    assert row is not None, f"Could not find table row for commit {commit_sha[:7]}"
    return row


@then('the index row for the commit should show an issue suggestion "{slug}"')
def step_index_row_shows_suggestion(context, slug):
    row = _find_row_for_current_commit(context)
    suggestion = row.find(attrs={"data-test": "issue-suggestion"})
    assert suggestion is not None, "Expected an issue suggestion helper on the row"
    link = suggestion.find("a", href=f"/issue/{slug}")
    assert link is not None, f"Expected suggestion helper to link to '/issue/{slug}'"
    assert link.text.strip() == slug, f"Expected suggestion link text '{slug}', saw '{link.text.strip()}'"
    button = suggestion.find("button", attrs={"data-issue": slug})
    assert button is not None, "Expected a button to apply the suggestion"
    assert button.text.strip().lower() == "use", "Expected button text 'Use'"


@then("the issue field for that commit should be blank")
def step_issue_field_blank_for_commit(context):
    row = _find_row_for_current_commit(context)
    input_el = row.find("input", attrs={"name": "issue"})
    assert input_el is not None, "Expected an issue input field on the row"
    value = input_el.get("value", "")
    assert value == "", f"Expected issue field to be blank, but it was '{value}'"


@then("the index row for the commit should not show an issue suggestion")
def step_index_row_no_suggestion(context):
    row = _find_row_for_current_commit(context)
    suggestion = row.find(attrs={"data-test": "issue-suggestion"})
    assert suggestion is None, "Did not expect an issue suggestion helper on the row"
