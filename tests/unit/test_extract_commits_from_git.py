import subprocess

from git_release_notes.utils.git import extract_commits_from_git


def test_extract_commits_with_touched_paths(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)

    # Create and commit a file
    test_file = repo / "test.txt"
    test_file.write_text("hello\n")
    subprocess.run(["git", "add", "test.txt"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo, check=True)

    # Extract commits
    commits = extract_commits_from_git(str(repo))
    assert len(commits) == 1
    commit = commits[0]

    assert "sha" in commit
    assert "message" in commit
    assert "touched_paths" in commit
    assert "test.txt" in commit["touched_paths"]
