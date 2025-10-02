"""
Test Plan: Tag Resolution Logic

This module verifies resolution of tag relationships in a Git commit graph.

Functions under test:
- find_follows_tag(): identifies the nearest preceding tag.
- find_precedes_tag(): identifies the nearest descendant tag.
- get_matching_tag_commits(): filters matching tags.
- get_topo_ordered_commits(): confirms topo sort matches rev-list.
- is_ancestor(): verifies ancestry relationship between commits.
- parse_describe_output(): parses `git describe` output.

Key behaviors tested:
- Tagged and untagged commits resolving to earlier/later tags
- Edge cases: no tags, multiple tags, out-of-pattern tags
- Symmetry between Follows and Precedes
"""
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

from tests.helpers.git_fixtures import create_tag, get_log_shas, test_repo
from git_release_notes.utils.git import find_follows_tag, find_precedes_tag


@pytest.mark.parametrize(
    "tag_map, target_index, expected_tag",
    [
        # Only the first commit is tagged
        ({"rel-0.1": 0}, 1, "rel-0.1"),  # middle follows rel-0.1
        ({"rel-0.1": 0}, 2, "rel-0.1"),  # latest follows rel-0.1

        # First and third commits are tagged
        ({"rel-0.1": 0, "rel-0.2": 2}, 1, "rel-0.1"),  # middle still follows rel-0.1
        ({"rel-0.1": 0, "rel-0.2": 2}, 2, "rel-0.1"),  # latest (tagged) still follows rel-0.1

        # Only third commit is tagged
        ({"rel-0.2": 2}, 1, None),  # middle has no preceding tag
        ({"rel-0.2": 2}, 2, None),  # latest has no preceding tag

        # No tags at all
        ({}, 1, None),
        ({}, 2, None),
    ]
)
def test_find_follows_tag(test_repo: Path, tag_map, target_index, expected_tag):
    """
    Verifies that find_follows_tag identifies the nearest preceding tag.

    - Tagged commits should still report the prior tag in Follows.
    - Untagged commits should report the most recent earlier tag.
    - Commits with no preceding tag should return None.
    - Covers cases with one, multiple, or no tags.
    """
    shas = get_log_shas(test_repo)

    for tag, index in tag_map.items():
        create_tag(test_repo, shas[index], tag)

    result = find_follows_tag(shas[target_index], str(test_repo), "rel-*")

    if expected_tag is None:
        assert result is None
    else:
        assert isinstance(result, SimpleNamespace)
        assert result.base_tag == expected_tag
        assert result.tag_sha == shas[tag_map[expected_tag]]


def test_find_follows_tag_returns_none_if_no_match(test_repo: Path):
    from git_release_notes.utils.git import find_follows_tag
    shas = get_log_shas(test_repo)
    # No tags at all
    result = find_follows_tag(shas[-1], str(test_repo), "rel-*")
    assert result is None


@pytest.mark.parametrize(
    "tag_map, target_index, expected_tag",
    [
        # Only the last commit is tagged
        ({"rel-0.2": 2}, 0, "rel-0.2"),  # initial precedes rel-0.2
        ({"rel-0.2": 2}, 1, "rel-0.2"),  # middle precedes rel-0.2

        # First and third commits are tagged
        ({"rel-0.1": 0, "rel-0.2": 2}, 1, "rel-0.2"),  # middle still precedes rel-0.2
        ({"rel-0.1": 0, "rel-0.2": 2}, 0, "rel-0.2"),  # rel-0.1 precedes rel-0.2

        # Only the first commit is tagged
        ({"rel-0.1": 0}, 1, None),  # middle has no descendant tag
        ({"rel-0.1": 0}, 2, None),  # latest has no descendant tag

        # No tags at all
        ({}, 0, None),
        ({}, 1, None),
    ]
)
def test_find_precedes_tag(test_repo: Path, tag_map, target_index, expected_tag):
    """
    Verifies that find_precedes_tag identifies the nearest descendant tag.

    - Both tagged and untagged commits should point to the next tag, if one exists.
    - Commits without any following tag should return None.
    - Covers cases with one, multiple, or no tags.
    """
    shas = get_log_shas(test_repo)

    for tag, index in tag_map.items():
        create_tag(test_repo, shas[index], tag)

    result = find_precedes_tag(shas[target_index], str(test_repo), "rel-*")

    if expected_tag is None:
        assert result is None
    else:
        assert isinstance(result, SimpleNamespace)
        assert result.base_tag == expected_tag
        assert result.tag_sha == shas[tag_map[expected_tag]]


def test_find_precedes_tag_returns_none_if_no_descendant_match(test_repo: Path):
    from git_release_notes.utils.git import find_precedes_tag
    shas = get_log_shas(test_repo)
    # Only tag the first commit
    create_tag(test_repo, shas[0], "rel-0.1")
    result = find_precedes_tag(shas[-1], str(test_repo), "rel-*")
    assert result is None


def test_get_matching_tag_commits(test_repo: Path):
    shas = get_log_shas(test_repo)
    create_tag(test_repo, shas[1], "rel-1")
    create_tag(test_repo, shas[2], "foo-2")  # Should not match

    from git_release_notes.utils.git import get_matching_tag_commits
    result = get_matching_tag_commits(str(test_repo), "rel-*")

    assert isinstance(result, dict)
    assert len(result) == 1
    assert shas[1] in result
    assert result[shas[1]] == "rel-1"


def test_get_topo_ordered_commits(test_repo: Path):
    from git_release_notes.utils.git import get_topo_ordered_commits
    topo = get_topo_ordered_commits(str(test_repo))
    assert isinstance(topo, list)
    assert len(topo) >= 3
    assert topo == get_log_shas(test_repo)


def test_is_ancestor(test_repo: Path):
    from git_release_notes.utils.git import is_ancestor
    shas = get_log_shas(test_repo)
    assert is_ancestor(shas[0], shas[2], str(test_repo)) is True
    assert is_ancestor(shas[2], shas[0], str(test_repo)) is False


def test_parse_describe_output():
    from git_release_notes.utils.git import parse_describe_output
    assert parse_describe_output("v1.2.3-4-gabcdef0") == ("v1.2.3", 4)
    assert parse_describe_output("rel-2-5-7-1-gabc1234") == ("rel-2-5-7", 1)
    assert parse_describe_output("v1.2.3") is None
