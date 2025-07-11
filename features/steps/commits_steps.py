"""Steps for commits.feature."""

import requests
from behave import given, when, then  # pylint: disable=no-name-in-module
from hamcrest import assert_that, contains_string, equal_to, not_

# pylint: disable=missing-function-docstring


@given('a known commit "{commit_label}"')
def step_known_commit_sha(context, commit_label):
    sha_map = {
        "initial": context.fixture_repo.shas[0],
        "middle": context.fixture_repo.shas[1],
        "latest": context.fixture_repo.shas[2],
    }
    context.commit_sha = sha_map[commit_label]


@when("I GET the detail page for that commit")
def step_get_commit_detail(context):
    url = f"{context.base_url}/commit/{context.commit_sha}"
    context.response = requests.get(url, timeout=5)


@then('the page should show follows "{follows_tag}"')
def step_response_shows_follows(context, follows_tag):
    assert_that(context.response.status_code, equal_to(200))
    if follows_tag == "(none)":
        assert_that(context.response.text, not_(contains_string("Follows:")))
    else:
        expected_target_sha = context.fixture_repo.tag_to_sha[follows_tag]
        assert_that(context.response.text, contains_string("Follows:"))
        assert_that(context.response.text, contains_string(follows_tag))
        assert_that(context.response.text, contains_string(expected_target_sha))


@then('the page should show precedes "{precedes_tag}"')
def step_response_shows_precedes(context, precedes_tag):
    if precedes_tag == "(none)":
        assert_that(context.response.text, not_(contains_string("Precedes:")))
    else:
        expected_target_sha = context.fixture_repo.tag_to_sha[precedes_tag]
        assert_that(context.response.text, contains_string("Precedes:"))
        assert_that(context.response.text, contains_string(precedes_tag))
        assert_that(context.response.text, contains_string(expected_target_sha))
