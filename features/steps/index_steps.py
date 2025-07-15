"""Steps for index.feature."""

import requests
from behave import given, when, then  # pylint: disable=no-name-in-module
from hamcrest import assert_that, equal_to, is_not, none

# pylint: disable=missing-function-docstring


@given("the server is running")
def step_server_running(context):
    assert_that(context.server, is_not(none()))


@given("the server is running without a spreadsheet")
def step_impl(context):
    assert_that(context.server.mode, matcher=equal_to("no_xlsx"))


@when("I GET the root page")
def step_get_root(context):
    context.response = requests.get(f"{context.server.base_url}/", timeout=5)


@then('the response should contain "{text}"')
def step_response_contains(context, text):
    assert context.response.status_code == 200
    assert text in context.response.text
