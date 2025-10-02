from pathlib import Path

from git_release_notes.handlers.issue import find_issue_file

def test_find_issue_file_finds_open(tmp_path):
    issues_dir = tmp_path / "issues"
    open_path = issues_dir / "open" / "foo.md"
    open_path.parent.mkdir(parents=True)
    open_path.write_text("test", encoding="utf-8")

    found = find_issue_file("foo", issues_dir)
    assert found == open_path

def test_find_issue_file_prefers_open_when_both_exist(tmp_path):
    issues_dir = tmp_path / "issues"
    open_path = issues_dir / "open" / "bar.md"
    closed_path = issues_dir / "closed" / "bar.md"
    open_path.parent.mkdir(parents=True)
    closed_path.parent.mkdir(parents=True)
    open_path.write_text("open", encoding="utf-8")
    closed_path.write_text("closed", encoding="utf-8")

    found = find_issue_file("bar", issues_dir)
    assert found == open_path

def test_find_issue_file_returns_closed_if_only_closed_exists(tmp_path):
    issues_dir = tmp_path / "issues"
    closed_path = issues_dir / "closed" / "baz.md"
    closed_path.parent.mkdir(parents=True)
    closed_path.write_text("closed", encoding="utf-8")

    found = find_issue_file("baz", issues_dir)
    assert found == closed_path

def test_find_issue_file_returns_none_if_missing(tmp_path):
    issues_dir = tmp_path / "issues"
    found = find_issue_file("nope", issues_dir)
    assert found is None
