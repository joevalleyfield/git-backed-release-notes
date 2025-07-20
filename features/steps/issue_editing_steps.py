"""Steps for enable_file_edit_no_xlsx.feature."""

import requests
from pathlib import Path

from behave import given, when, then  # pylint: disable=no-name-in-module
from hamcrest import assert_that, contains_string, equal_to

import pandas as pd

from features.support.issue_helpers import create_issue_file, make_commit_with_message

# pylint: disable=missing-function-docstring

@given('the issues directory contains an open issue "{slug}"')
def step_impl(context, slug):
    create_issue_file(context.repo_path, slug)
    context.issue_slug = slug

@given('the Git repository contains a commit "{msg}"')
def step_impl(context, msg):
    context.commit_sha = make_commit_with_message(msg, context.repo_path)

@when('the user changes the "{field}" field to "{value}"')
def step_impl(context, field, value):
    slug = context.issue_slug
    path: Path = context.repo_path / "issues/open" / f"{slug}.md"
    lines = path.read_text(encoding="utf-8").splitlines()
    updated = []
    found = False
    for line in lines:
        if line.startswith(f"{field}:"):
            updated.append(f"{field}: {value}")
            found = True
        else:
            updated.append(line)
    if not found:
        updated.append(f"{field}: {value}")

    context.edited_issue_slug = slug
    context.edited_issue_content = "\n".join(updated) + "\n"

@then('the issue file "{slug}.md" should contain "{text}"')
def step_impl(context, slug, text):
    with open(context.repo_path / f"issues/open/{slug}.md", encoding="utf-8") as f:
        assert text in f.read()

@when('the user visits the issue "{slug}" detail page')
def step_impl(context, slug):
    url = f"{context.server.base_url}/issue/{slug}"
    context.response = requests.get(url, timeout=5)
    assert context.response.status_code == 200

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
    assert sha in response.text  # or check for SHA in the future


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