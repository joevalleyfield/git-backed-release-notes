"""
Git utility functions for extracting commit metadata from a local repository.

Includes:
- extract_commits_from_git: fallback data source when no spreadsheet is provided.
- get_commit_parents_and_children: Return the parent and child SHAs for a given commit.
"""
from functools import lru_cache
import subprocess
from typing import List, Tuple


def extract_commits_from_git(repo_path: str) -> list[dict]:
    """
    Extract commit metadata directly from the Git repository.

    Returns a list of dictionaries with keys: id, sha, release, message, and author_date.
    Used when no spreadsheet is provided.
    """
    result = subprocess.run(
        [
            "git",
            "-C",
            repo_path,
            "log",
            "--pretty=format:%H%x09%ad%x09%s",
            "--date=iso",
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    rows = []
    for idx, line in enumerate(result.stdout.strip().splitlines()):
        sha, author_date, message = line.split("\t", 2)
        rows.append(
            {
                "id": idx,
                "sha": sha,
                "release": "",  # no spreadsheet = no release label
                "message": message,
                "author_date": author_date,
            }
        )
    return rows


@lru_cache(maxsize=None)
def get_commit_parents_and_children(sha: str, repo_path: str) -> Tuple[List[str], List[str]]:
    """
    Return the parent and child SHAs for a given commit.

    - Parents are obtained directly via `git show`.
    - Children are computed by scanning `git rev-list --all --children`.

    Results are cached by (sha, repo_path).
    """
    parents = _get_parents(sha, repo_path)
    children = _get_children_map(repo_path).get(sha, [])
    return parents, children


def _get_parents(sha: str, repo_path: str) -> List[str]:
    result = subprocess.run(
        ["git", "show", "-s", "--format=%P", sha],
        capture_output=True,
        text=True,
        check=True,
        cwd=repo_path,
    )
    return result.stdout.strip().split()


@lru_cache(maxsize=1)
def _get_children_map(repo_path: str) -> dict:
    """
    Build a mapping of commit SHA to its list of children.
    Only called once per repo_path (due to lru_cache).
    """
    result = subprocess.run(
        ["git", "rev-list", "--all", "--children"],
        capture_output=True,
        text=True,
        check=True,
        cwd=repo_path,
    )

    children_map = {}
    for line in result.stdout.strip().splitlines():
        parts = line.strip().split()
        if len(parts) > 1:
            parent, *children = parts
            children_map[parent] = children
    return children_map
