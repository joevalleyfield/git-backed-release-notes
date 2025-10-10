"""Steps for edit_from_index.feature."""

import requests
from behave import then, when
from bs4 import BeautifulSoup
from hamcrest import assert_that, contains_string, equal_to, is_not, none


@when('I submit a new issue slug "{slug}" for that commit via the index form')
def step_submit_issue_from_index(context, slug):
    # Target the commit seeded with the "allow-editing" issue slug
    sha = context.fixture_repo.issue_map["allow-editing"]
    context.commit_sha = sha
    context.response = requests.post(
        f"{context.server.base_url}/commit/{sha}/update",
        data={"issue": slug},
        timeout=30,
    )


@when('I submit a new release value "{value}" for that commit via the index form')
def step_submit_release_from_index(context, value):
    sha = context.fixture_repo.sha_map["initial"]
    context.commit_sha = sha
    context.response = requests.post(
        f"{context.server.base_url}/commit/{sha}/update",
        data={"release": value},
        timeout=30,
    )


@then('the response should contain the updated issue slug "{slug}"')
def step_response_contains_issue_slug(context, slug):
    assert_that(context.response.status_code, equal_to(200))
    assert_that(context.response.text, contains_string(slug))


@then('the response should contain the updated release value "{value}"')
def step_response_contains_release_value(context, value):
    assert_that(context.response.status_code, equal_to(200))
    assert_that(context.response.text, contains_string(value))


@then('the response should contain a form field "{field}" for commit "{commit_label}"')
def step_form_field_present_for_commit(context, field, commit_label):
    sha = context.fixture_repo.sha_map[commit_label]
    soup = BeautifulSoup(context.response.text, "html.parser")

    # form is now separate and referenced by ID
    form_id = f"form-{sha}"
    form = soup.find("form", attrs={"id": form_id})
    assert_that(form, is_not(none()), f"No form with id='{form_id}'")

    # input is inside the table, but associated via form="..."
    input_field = soup.find("input", attrs={"name": field, "form": form_id})
    assert_that(input_field, is_not(none()), f"No input for '{field}' with form='{form_id}'")
