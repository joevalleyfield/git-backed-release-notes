"""
Git utility functions for extracting commit metadata from a local repository.

Includes:
- extract_commits_from_git: fallback data source when no spreadsheet is provided.
"""
import subprocess

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
