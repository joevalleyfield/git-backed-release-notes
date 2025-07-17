"""Steps for commits.feature."""

import requests

from behave import when, then  # pylint: disable=no-name-in-module
from hamcrest import assert_that, contains_string, equal_to

import pandas as pd

# pylint: disable=missing-function-docstring


@when('I submit a new issue slug "{slug}" for that commit')
def step_submit_issue_slug(context, slug):
    sha = context.commit_sha
    context.response = requests.post(
        f"{context.server.base_url}/commit/{sha}/update",
        data={"issue": slug},
        timeout=60,
    )


@then('the commit page should show the updated issue slug "{slug}"')
def step_commit_page_shows_issue(context, slug):
    assert_that(context.response.status_code, equal_to(200))
    assert_that(context.response.text, contains_string(slug))


@then('the spreadsheet should contain the issue slug "{slug}" for that commit')
def step_excel_contains_updated_issue(context, slug):

    df = pd.read_excel(context.xlsx_path).fillna("")
    sha = context.commit_sha
    matches = df[df["sha"] == sha]
    assert_that(matches.empty, equal_to(False), f"No row found for sha {sha}")
    issue_value = matches.iloc[0]["issue"]
    assert_that(issue_value, equal_to(slug))


@then("the response status should be {code:d}")
def step_response_status_code(context, code):
    assert_that(context.response.status_code, equal_to(code))
