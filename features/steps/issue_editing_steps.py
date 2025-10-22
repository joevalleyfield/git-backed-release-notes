"""Steps for enable_file_edit_no_xlsx.feature."""

import requests
from behave import given, then, when  # pylint: disable=no-name-in-module
from bs4 import BeautifulSoup
from features.support.git_helpers import create_commit, create_commit_touching_issue
from features.support.issue_helpers import create_issue_file, link_commit_to_issue
from hamcrest import assert_that, contains_string

# pylint: disable=missing-function-docstring


@given('the commit is linked to issue "{slug}"')
def step_link_fixture_commit(context, slug):
    sha = context.commit_sha
    link_commit_to_issue(context.repo_path, sha, slug)


@given('the issues directory contains an open issue "{slug}"')
def step_create_open_issue(context, slug):
    create_issue_file(context.repo_path, slug)
    context.issue_slug = slug


@given('the Git repository contains a commit "{msg}"')
def step_create_commit_with_message(context, msg):
    context.commit_sha = create_commit(context.repo_path, msg)


@given('the Git repository contains a commit touching issue "{slug}" with message "{msg}"')
def step_create_commit_touching_issue(context, slug, msg):
    context.commit_sha = create_commit_touching_issue(context.repo_path, slug, msg)


@then('the issue file "{slug}.md" should contain "{text}"')
def step_assert_issue_file_contains(context, slug, text):
    with open(context.repo_path / f"issues/open/{slug}.md", encoding="utf-8") as f:
        assert text in f.read()


@when('the user visits the issue "{slug}" detail page')
def step_visit_issue_detail(context, slug):
    url = f"{context.server.base_url}/issue/{slug}"
    context.response = requests.get(url, timeout=5)
    assert context.response.status_code == 200


@when('the user visits the commit detail page for "{_}"')
def step_visit_commit_detail(context, _):
    # We're ignoring the message string in Gherkin — context.commit_sha
    # is authoritative
    url = f"{context.server.base_url}/commit/{context.commit_sha}"
    context.response = requests.get(url, timeout=5)


@then('the issue "{slug}" should show the commit "{message}"')
def step_issue_page_shows_commit(context, slug, message):
    sha = context.commit_sha
    url = f"{context.server.base_url}/issue/{slug}"
    response = requests.get(url, timeout=5)
    assert response.status_code == 200
    assert_that(response.text, contains_string(sha))
    assert_that(response.text, contains_string(message))


@when('the user links the commit to issue "{slug}"')
def step_link_commit_via_form(context, slug):
    sha = context.commit_sha
    context.response = requests.post(
        f"{context.server.base_url}/commit/{sha}/update",
        data={"issue": slug},
        timeout=60,
    )
    assert context.response.status_code in (200, 302)


@then("a metadata file should record the link between the commit and issue")
def step_assert_metadata_file_updated(context):
    commit_sha: str = context.commit_sha
    metadata_path = context.repo_path / "git-view.metadata.csv"
    assert metadata_path.exists()

    import pandas as pd

    df = pd.read_csv(metadata_path)
    match = df[df["sha"] == commit_sha]
    assert not match.empty
    assert match.iloc[0]["issue"] == "foo-bar"


@then('I should see a link to "{url}"')
def step_assert_link_present(context, url):
    soup = BeautifulSoup(context.response.text, "html.parser")
    match = soup.find("a", href=url)
    assert match is not None, f"Expected link to {url} not found"


@then('the issue field should be prefilled with "{slug}"')
def step_issue_field_prefilled(context, slug):
    soup = BeautifulSoup(context.response.text, "html.parser")
    issue_input = soup.find("input", attrs={"name": "issue"})
    assert issue_input is not None, "Expected an input named 'issue' on the page"
    value = issue_input.get("value", "")
    assert value == slug, f"Expected issue field to be prefilled with '{slug}', but it was '{value}'"


@then('the issue suggestion helper should link to "{slug}"')
def step_issue_suggestion_helper_links(context, slug):
    soup = BeautifulSoup(context.response.text, "html.parser")
    suggestion = soup.find(id="issue-suggestion")
    assert suggestion is not None, "Expected an issue suggestion helper on the page"
    link = suggestion.find("a", href=f"/issue/{slug}")
    assert link is not None, f"Expected suggestion helper to link to '/issue/{slug}'"
    assert link.text.strip() == slug, f"Expected suggestion link text '{slug}', saw '{link.text.strip()}'"


@then('I should see an issue suggestion button for "{slug}"')
def step_issue_suggestion_button_present(context, slug):
    soup = BeautifulSoup(context.response.text, "html.parser")
    button = soup.find(id="issue-suggestion-apply")
    assert button is not None, "Expected a suggestion apply button"
    text = button.get_text(strip=True)
    assert text == "Use", f"Expected button text 'Use', saw '{text}'"
    assert (
        button.get("data-issue", "") == slug
    ), f"Expected button data-issue '{slug}', saw '{button.get('data-issue', '')}'"


@then("the issue field should be blank")
def step_issue_field_blank(context):
    soup = BeautifulSoup(context.response.text, "html.parser")
    issue_input = soup.find("input", attrs={"name": "issue"})
    assert issue_input is not None, "Expected an input named 'issue' on the page"
    value = issue_input.get("value", "")
    assert value == "", f"Expected issue field to be blank, but it was '{value}'"


@then("no issue suggestion helper should be shown")
def step_no_issue_suggestion_helper(context):
    soup = BeautifulSoup(context.response.text, "html.parser")
    suggestion = soup.find(id="issue-suggestion")
    assert suggestion is None, "Did not expect an issue suggestion helper to be shown"


@when('the user updates the issue content to include "{text}"')
def step_prepare_issue_edit(context, text):
    slug = context.issue_slug

    soup = BeautifulSoup(context.response.text, "html.parser")
    textarea = soup.find("textarea", attrs={"name": "markdown"})
    assert textarea is not None, "Expected a textarea named 'markdown' in the response"

    body = textarea.text + f"\n{text}\n"
    context.edited_issue_slug = slug
    context.edited_issue_content = body


@when("the user saves the issue")
def step_submit_issue_update(context):
    slug = context.edited_issue_slug
    body = context.edited_issue_content
    url = f"{context.server.base_url}/issue/{slug}/update"

    context.response = requests.post(
        url,
        data={"markdown": body},
        timeout=5,
    )


@given('the issues directory contains a closed issue "{slug}"')
def step_create_closed_issue(context, slug):
    create_issue_file(context.repo_path, slug, closed=True)
    context.issue_slug = slug


@then('the closed issue file "{slug}.md" should contain "{text}"')
def step_assert_closed_issue_file(context, slug, text):
    with open(context.repo_path / f"issues/closed/{slug}.md", encoding="utf-8") as f:
        assert text in f.read()


@given('an uncommitted issue file named "{filename}" with contents:')
def step_create_uncommitted_issue_file(context, filename):
    path = context.repo_path / "issues" / "open" / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(context.text, encoding="utf-8")
