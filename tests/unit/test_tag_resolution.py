import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

from utils.git import find_follows_tag, find_precedes_tag


@pytest.fixture
def test_repo(tmp_path: Path) -> Path:
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


def get_log_shas(repo: Path) -> list[str]:
    result = subprocess.run(
        ["git", "rev-list", "--reverse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
        cwd=repo,
    )
    return result.stdout.strip().splitlines()


def create_tag(repo: Path, sha: str, tagname: str):
    subprocess.run(["git", "tag", tagname, sha], cwd=repo, check=True)


def test_find_follows_tag(test_repo: Path):
    shas = get_log_shas(test_repo)
    create_tag(test_repo, shas[0], "rel-0.1")

    result = find_follows_tag(shas[1], str(test_repo), "rel-*")
    assert isinstance(result, SimpleNamespace)
    assert result.base_tag == "rel-0.1"
    assert result.count == 1
    assert result.tag_sha == shas[0]


def test_find_precedes_tag(test_repo: Path):
    shas = get_log_shas(test_repo)
    create_tag(test_repo, shas[2], "rel-0.2")

    result = find_precedes_tag(shas[1], str(test_repo), "rel-*")
    assert isinstance(result, SimpleNamespace)
    assert result.base_tag == "rel-0.2"
    assert result.tag_sha == shas[2]
