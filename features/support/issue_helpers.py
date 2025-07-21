from pathlib import Path

import pandas as pd

from features.environment import create_commit  # if environment.py exports it

def make_commit_with_message(message: str, repo_path: Path = Path(".")) -> str:
    """Wrapper to create a commit for the current test repo."""
    return create_commit(repo_path, message)

def create_issue_file(repo_path: Path, slug: str, status: str = "open", body: str = "") -> None:
    base_dir = repo_path / "issues" / status
    base_dir.mkdir(parents=True, exist_ok=True)
    path = base_dir / f"{slug}.md"
    with path.open("w", encoding="utf-8") as f:
        f.write(f"# {slug.replace('-', ' ').title()}\n")
        f.write(f"status: {status}\n")
        if body:
            f.write("\n" + body + "\n")

def link_commit_to_issue(repo_path: Path, sha: str, issue_slug: str) -> None:
    metadata_path = repo_path / "git-view.metadata.csv"
    if metadata_path.exists():
        df = pd.read_csv(metadata_path)
    else:
        df = pd.DataFrame(columns=["sha", "issue", "release"])

    if sha in df["sha"].values:
        df.loc[df["sha"] == sha, "issue"] = issue_slug
    else:
        df.loc[len(df)] = [sha, issue_slug, ""]

    df.to_csv(metadata_path, index=False)
