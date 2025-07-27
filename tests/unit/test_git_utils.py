import subprocess
from pathlib import Path
import pytest

from utils.git import get_commit_parents_and_children


@pytest.fixture
def test_repo(tmp_path: Path) -> Path:
    subprocess.run(["git", "init"], cwd=tmp_path, check=True)
    (tmp_path / "file.txt").write_text("a\n")
    subprocess.run(["git", "add", "file.txt"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=tmp_path, check=True)

    (tmp_path / "file.txt").write_text("b\n")
    subprocess.run(["git", "commit", "-am", "second"], cwd=tmp_path, check=True)

    (tmp_path / "file.txt").write_text("c\n")
    subprocess.run(["git", "commit", "-am", "third"], cwd=tmp_path, check=True)

    return tmp_path


def get_log_shas(repo: Path) -> list[str]:
    result = subprocess.run(
        ["git", "rev-list", "--reverse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
        cwd=repo,
    )
    return result.stdout.strip().splitlines()


def test_commit_graph_extraction(test_repo: Path):
    shas = get_log_shas(test_repo)
    print(shas)
    sha0, sha1, sha2 = shas

    # SHA1 is child of SHA0
    parents, children = get_commit_parents_and_children(sha1, str(test_repo))
    assert parents == [sha0]
    assert sha2 in children

    # SHA0 is root, has no parents
    parents0, children0 = get_commit_parents_and_children(sha0, str(test_repo))
    assert parents0 == []
    assert sha1 in children0
