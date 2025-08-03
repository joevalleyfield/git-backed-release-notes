"""
Git fixture helpers for test setup.

Provides shared functions and fixtures for initializing Git state
across unit and integration tests.
"""

import subprocess
from pathlib import Path

import pytest


def create_tag(repo: Path, sha: str, tagname: str):
    """Create a lightweight tag at the given commit SHA."""
    subprocess.run(["git", "tag", tagname, sha], cwd=repo, check=True)


def get_log_shas(repo: Path) -> list[str]:
    """Return all commit SHAs in rev-list --reverse order."""
    result = subprocess.run(
        ["git", "rev-list", "--reverse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
        cwd=repo,
    )
    return result.stdout.strip().splitlines()


@pytest.fixture
def test_repo(tmp_path: Path) -> Path:
    """Create a Git repo with 3 commits and return its path."""
    subprocess.run(["git", "init"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True)

    def commit(msg, content):
        (tmp_path / "file.txt").write_text(content)
        subprocess.run(["git", "add", "file.txt"], cwd=tmp_path, check=True)
        subprocess.run(["git", "commit", "-m", msg], cwd=tmp_path, check=True)

    commit("first", "a\n")
    commit("second", "b\n")
    commit("third", "c\n")

    return tmp_path