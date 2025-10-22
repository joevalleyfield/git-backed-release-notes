"""Steps for enable_file_edit_no_xlsx.feature."""

import requests
from behave import given, then, when  # pylint: disable=no-name-in-module
from bs4 import BeautifulSoup
from features.support.git_helpers import create_commit
from features.support.issue_helpers import create_issue_file, link_commit_to_issue
from hamcrest import assert_that, contains_string

# pylint: disable=missing-function-docstring


@given('the commit is linked to issue "foo-bar"')
def step_link_fixture_commit(context):
    sha = context.commit_sha
    link_commit_to_issue(context.repo_path, sha, "foo-bar")


@given('the issues directory contains an open issue "{slug}"')
def step_create_open_issue(context, slug):
    create_issue_file(context.repo_path, slug)
    context.issue_slug = slug


@given('the Git repository contains a commit "{msg}"')
def step_create_commit_with_message(context, msg):
    context.commit_sha = create_commit(context.repo_path, msg)


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
