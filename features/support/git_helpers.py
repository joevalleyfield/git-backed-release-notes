from pathlib import Path
import subprocess


def init_repo(repo_path: Path) -> None:
    """Initialize a Git repository with user config."""

    subprocess.run(["git", "init"], cwd=repo_path, check=True)
    subprocess.run(
        ["git", "config", "user.name", "Test User"], cwd=repo_path, check=True
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"], cwd=repo_path, check=True
    )


def create_commit(repo_path: Path, message: str) -> str:
    """Create a commit with the given message and return its SHA."""

    with open(repo_path / "file.txt", "a", encoding="utf-8") as f:
        f.write(f"{message}\n")
    subprocess.run(["git", "add", "."], cwd=repo_path, check=True)
    subprocess.run(["git", "commit", "-m", message], cwd=repo_path, check=True)
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


def tag_commit(repo_path: Path, sha: str, tag_name: str) -> None:
    """Create a lightweight tag pointing to the specified commit SHA."""

    subprocess.run(["git", "tag", tag_name, sha], cwd=repo_path, check=True)
