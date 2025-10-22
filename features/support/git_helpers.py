import subprocess
from pathlib import Path


def init_repo(repo_path: Path) -> None:
    """Initialize a Git repository with user config."""

    subprocess.run(["git", "init"], cwd=repo_path, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo_path, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo_path, check=True)


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


def create_commit_touching_issue(repo_path: Path, slug: str, message: str) -> str:
    """
    Create a commit that touches an issue Markdown file and return its SHA.

    Ensures the issue file exists (creating it if necessary), appends a marker line,
    and commits with the provided message so the diff references the issue path.
    """

    issue_dir = repo_path / "issues" / "open"
    issue_dir.mkdir(parents=True, exist_ok=True)
    issue_path = issue_dir / f"{slug}.md"

    if issue_path.exists():
        with issue_path.open("a", encoding="utf-8") as f:
            f.write("\n<!-- touched by test commit -->\n")
    else:
        with issue_path.open("w", encoding="utf-8") as f:
            f.write(f"# {slug.replace('-', ' ').title()}\n")
            f.write("status: open\n")
            f.write("\n<!-- created by test commit -->\n")

    rel_path = issue_path.relative_to(repo_path)
    subprocess.run(["git", "add", str(rel_path)], cwd=repo_path, check=True)
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
