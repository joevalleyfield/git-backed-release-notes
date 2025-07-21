"""Steps for enable_file_edit_no_xlsx.feature."""

import requests
from pathlib import Path

from behave import given, when, then  # pylint: disable=no-name-in-module
from bs4 import BeautifulSoup
from hamcrest import assert_that, contains_string, equal_to

import pandas as pd

from features.support.issue_helpers import (
    create_issue_file,
    link_commit_to_issue)

from features.support.git_helpers import create_commit

# pylint: disable=missing-function-docstring

@given('the commit is linked to issue "foo-bar"')
def step_impl(context):
    sha = context.commit_sha
    link_commit_to_issue(context.repo_path, sha, "foo-bar")  

@given('the issues directory contains an open issue "{slug}"')
def step_impl(context, slug):
    create_issue_file(context.repo_path, slug)
    context.issue_slug = slug

@given('the Git repository contains a commit "{msg}"')
def step_impl(context, msg):
    context.commit_sha = create_commit(context.repo_path, msg)

@then('the issue file "{slug}.md" should contain "{text}"')
def step_impl(context, slug, text):
    with open(context.repo_path / f"issues/open/{slug}.md", encoding="utf-8") as f:
        assert text in f.read()

@when('the user visits the issue "{slug}" detail page')
def step_impl(context, slug):
    url = f"{context.server.base_url}/issue/{slug}"
    context.response = requests.get(url, timeout=5)
    assert context.response.status_code == 200


@when('the user visits the commit detail page for "{_}"')
def step_impl(context, _):
    # We're ignoring the message string in Gherkin — context.commit_sha
    # is authoritative
    url = f"{context.server.base_url}/commit/{context.commit_sha}"
    context.response = requests.get(url, timeout=5)

@then('the issue "{slug}" should show the commit "{message}"')
def step_impl(context, slug, message):
    sha = context.commit_sha
    url = f"{context.server.base_url}/issue/{slug}"
    response = requests.get(url, timeout=5)
    assert response.status_code == 200
    assert_that(response.text, contains_string(sha))

@when('the user links the commit to issue "{slug}"')
def step_impl(context, slug):
    sha = context.commit_sha
    context.response = requests.post(
        f"{context.server.base_url}/commit/{sha}/update",
        data={"issue": slug},
        timeout=60,
    )
    assert context.response.status_code in (200, 302)


@then('a metadata file should record the link between the commit and issue')
def step_impl(context):
    commit_sha: str = context.commit_sha
    metadata_path = context.repo_path / "git-view.metadata.csv"
    assert metadata_path.exists()

    import pandas as pd
    df = pd.read_csv(metadata_path)
    match = df[df["sha"] == commit_sha]
    assert not match.empty
    assert match.iloc[0]["issue"] == "foo-bar"


@then('I should see a link to "/issue/foo-bar" with text "foo-bar"')
def step_impl(context):
    soup = BeautifulSoup(context.response.text, "html.parser")
    match = soup.find("a", href="/issue/foo-bar", string="foo-bar")
    assert match is not None, "Expected link to /issue/foo-bar with text 'foo-bar' not found"


@when('the user updates the issue content to include "{text}"')
def step_impl(context, text):
    slug = context.issue_slug
    path: Path = context.repo_path / "issues/open" / f"{slug}.md"
    body = path.read_text(encoding="utf-8") + f"\n{text}\n"
    context.edited_issue_slug = slug
    context.edited_issue_content = body

@when('the user saves the issue')
def step_impl(context):
    slug = context.edited_issue_slug
    body = context.edited_issue_content
    url = f"{context.server.base_url}/issue/{slug}/update"

    print(context.edited_issue_content)
    context.response = requests.post(
        url,
        data={"markdown": body},
        timeout=5,
    )
