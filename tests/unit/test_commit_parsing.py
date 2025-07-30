import pytest
from utils.commit_parsing import extract_issue_slugs


import re
import pytest
from utils.commit_parsing import extract_issue_slugs, DIRECTIVE_RE, SLUG_RE


@pytest.mark.parametrize(
    "message, expected_primary, expected_all",
    [
        ("Fixes #foo", "foo", ["foo"]),
        ("Fixes: #foo and #bar", "foo", ["foo", "bar"]),
        ("Implements #alpha\nAlso resolves #beta\nRelates to #gamma", "alpha", ["alpha", "beta", "gamma"]),
        ("This is just some text #not-a-directive", None, ["not-a-directive"]),
        ("Touch nothing", None, []),
    ],
)
def test_extract_issue_slugs(message, expected_primary, expected_all):
    primary, all_slugs = extract_issue_slugs(message)
    assert primary == expected_primary
    assert all_slugs == expected_all


import pytest

@pytest.mark.parametrize("text, expected_verb, expected_slug", [
    # ✅ Valid directive cases
    ("Fixes #foo", "Fixes", "foo"),
    ("fixes bar.md", "fixes", "bar"),
    ("Closes: #baz", "Closes", "baz"),
    ("Implemented qux.md", "Implemented", "qux"),
    ("Resolves foo-bar", "Resolves", "foo-bar"),
    ("Fixes #foo-bar.md", "Fixes", "foo-bar"),
    # ❌ Invalid or rejected cases
    ("Fixes #Foo", None, None),            # uppercase
    ("Fixes BARE.md", None, None),         # uppercase
    ("Mentions foo", None, None),          # not a directive
    ("#foo-bar.md is fixed", None, None),  # no directive
    ("Fixes foo.HTML", None, None),        # invalid extension
    ("Fixes #", None, None),               # empty slug
])
def test_directive_re_primary_match(text, expected_verb, expected_slug):
    m = DIRECTIVE_RE.search(text)
    if expected_verb is None:
        assert not m
    else:
        assert m
        assert m.group("verb") == expected_verb
        assert m.group("slug") == expected_slug


import re

@pytest.mark.parametrize("text, expected", [
    ("Fixes #bare", ["bare"]),
    ("Touches bare.md", ["bare"]),
    ("Mentions #bare.md", ["bare"]),
    ("Implements foo-bar", ["foo-bar"]),
    ("Has a ball with foo-bar-baz and #spike", ["foo-bar-baz", "spike"]),
    ("Touch nothing", []),
    ("References to qux and #zap.md", ["zap"]),  # Only zap.md is valid
])
def test_slug_re(text, expected):
    matches = []
    for m in SLUG_RE.finditer(text):
        for val in m.groups():
            if val:
                matches.append(val)
                break
    assert matches == expected