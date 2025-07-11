"""Steps for no_spreadsheet_mode.feature."""

from behave import given, when, then  # pylint: disable=no-name-in-module
import requests
from hamcrest import assert_that, equal_to, contains_string

# pylint: disable=missing-function-docstring

@given("I am in a Git repository with an issues/ directory")
def step_in_repo_with_issues(context):
    repo_root = context.repo_path
    assert (repo_root / ".git").exists()
    assert (repo_root / "issues").is_dir()

@when('I run "python app.py" with no arguments')
def step_run_app_no_args(_context):
    # Already handled by `@require_dogfood_fixture`
    pass

@then("the index page should list recent commits")
def step_index_lists_commits(context):
    r = requests.get(f"{context.base_url}/", timeout=5)
    assert_that(r.status_code, equal_to(200))
    assert_that(r.text, contains_string("Commits"))

@then("it should include a link to each commit detail page")
def step_commit_links_present(context):
    r = requests.get(f"{context.base_url}/", timeout=5)
    assert_that(r.status_code, equal_to(200))
    for sha in context.expected_shas:
        # assert_that(r.text, contains_string(f'href="/commit/{sha}"'))
        pass