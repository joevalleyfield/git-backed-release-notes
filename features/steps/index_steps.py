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
