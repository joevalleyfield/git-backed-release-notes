from types import SimpleNamespace

from git_release_notes.utils.issues import find_commits_referring_to_issue

def make_row(**kwargs):
    return SimpleNamespace(
        sha=kwargs.get("sha", "deadbeef"),
        message=kwargs.get("message", ""),
        issue=kwargs.get("issue"),
        touched_paths=kwargs.get("touched_paths", []),
    )

def test_explicit_match_via_issue_field():
    commits = [make_row(issue="my-feature")]
    result = find_commits_referring_to_issue("my-feature", commits)
    assert len(result) == 1
    assert result[0].issue == "my-feature"

def test_directive_match_via_message():
    commits = [make_row(message="Fixes #my-feature")]
    result = find_commits_referring_to_issue("my-feature", commits)
    assert len(result) == 1

def test_touching_issue_file_open_dir():
    commits = [make_row(touched_paths=["issues/open/my-feature.md"])]
    result = find_commits_referring_to_issue("my-feature", commits)
    assert len(result) == 1

def test_touching_issue_file_closed_dir():
    commits = [make_row(touched_paths=["issues/closed/my-feature.md"])]
    result = find_commits_referring_to_issue("my-feature", commits)
    assert len(result) == 1

def test_no_match():
    commits = [make_row(message="unrelated commit")]
    result = find_commits_referring_to_issue("my-feature", commits)
    assert len(result) == 0
