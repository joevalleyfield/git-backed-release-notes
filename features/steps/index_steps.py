"""Steps for index.feature."""

import requests
from behave import given, when, then  # pylint: disable=no-name-in-module

# pylint: disable=missing-function-docstring

@given("the server is running")
def step_server_running(context):
    context.base_url = "http://localhost:8888"  # assume already running

@when("I GET the root page")
def step_get_root(context):
    context.response = requests.get(f"{context.base_url}/", timeout=5)

@then('the response should contain "{text}"')
def step_response_contains(context, text):
    assert context.response.status_code == 200
    assert text in context.response.text
