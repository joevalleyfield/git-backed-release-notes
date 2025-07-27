"""Steps for commits.feature."""

import requests
from behave import given, when, then  # pylint: disable=no-name-in-module
from hamcrest import assert_that, contains_string, equal_to, is_not, none, not_
from bs4 import BeautifulSoup

from utils.git import get_commit_parents_and_children

# pylint: disable=missing-function-docstring


@given('a known commit "{commit_label}" with issue "{issue_slug}"')
def step_known_commit_with_issue(context, commit_label, issue_slug):
    context.commit_sha = context.fixture_repo.sha_map[commit_label]


@given('a known commit "{commit_label}"')
def step_known_commit_sha(context, commit_label):
    context.commit_sha = context.fixture_repo.sha_map[commit_label]



@when("I GET the detail page for that commit")
def step_get_commit_detail(context):
    url = f"{context.server.base_url}/commit/{context.commit_sha}"
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


@then("the page should have a back link to the index anchor for that commit")
def step_check_back_link_anchor(context):
    soup = BeautifulSoup(context.response.text, "html.parser")
    back_link = soup.find("a", id="back-link")
    assert_that(back_link, is_not(none()), "Back link not found")
    expected_href = f"/#sha-{context.commit_sha[:7]}"
    assert_that(back_link["href"], equal_to(expected_href))


@then("the page should contain a metadata form with an issue field")
def step_impl(context):
    assert '<label for="issue"' in context.response.text
    assert 'name="issue"' in context.response.text


@then("the page should contain a metadata form with a release field")
def step_impl(context):
    assert '<label for="release"' in context.response.text
    assert 'name="release"' in context.response.text

@then('the page should contain a link labeled "{label}"')
def step_impl(context, label):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(context.response.text, "html.parser")
    links = soup.find_all("a")
    assert any(label in link.text for link in links), f"Expected link labeled '{label}' not found."

@then("the page should contain a link to the parent of that commit")
def step_impl(context):
    sha = context.commit_sha
    repo = context.repo_path
    parents, _ = get_commit_parents_and_children(sha, str(repo))

    soup = BeautifulSoup(context.response.text, "html.parser")
    link_hrefs = [a["href"] for a in soup.find_all("a", href=True)]
    for p in parents:
        expected = f"/commit/{p}"
        assert expected in link_hrefs, f"Missing link to parent: {expected}"
