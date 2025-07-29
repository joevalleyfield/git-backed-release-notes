import pytest
from utils.commit_parsing import extract_issue_slugs


@pytest.mark.parametrize(
    "message, expected_primary, expected_all",
    [
        (
            "Fixes #foo",
            "foo",
            ["foo"]
        ),
        (
            "Fixes: #foo and #bar",
            "foo",
            ["foo", "bar"]
        ),
        (
            "Implements #alpha\nAlso resolves #beta\nRelates to #gamma",
            "alpha",
            ["alpha", "beta", "gamma"]
        ),
        (
            "This is just some text #not-a-directive",
            None,
            ["not-a-directive"]
        ),
        (
            "Touch nothing",
            None,
            []
        ),
    ],
)
def test_extract_issue_slugs(message, expected_primary, expected_all):
    primary, all_slugs = extract_issue_slugs(message)
    assert primary == expected_primary
    assert all_slugs == expected_all