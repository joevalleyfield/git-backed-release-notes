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


def test_find_follows_tag_returns_none_if_no_match(test_repo: Path):
    from utils.git import find_follows_tag
    shas = get_log_shas(test_repo)
    # No tags at all
    result = find_follows_tag(shas[-1], str(test_repo), "rel-*")
    assert result is None


def test_find_precedes_tag(test_repo: Path):
    shas = get_log_shas(test_repo)
    create_tag(test_repo, shas[2], "rel-0.2")

    result = find_precedes_tag(shas[1], str(test_repo), "rel-*")
    assert isinstance(result, SimpleNamespace)
    assert result.base_tag == "rel-0.2"
    assert result.tag_sha == shas[2]


def test_find_precedes_tag_returns_none_if_no_descendant_match(test_repo: Path):
    from utils.git import find_precedes_tag
    shas = get_log_shas(test_repo)
    # Only tag the first commit
    create_tag(test_repo, shas[0], "rel-0.1")
    result = find_precedes_tag(shas[-1], str(test_repo), "rel-*")
    assert result is None


def test_get_matching_tag_commits(test_repo: Path):
    shas = get_log_shas(test_repo)
    create_tag(test_repo, shas[1], "rel-1")
    create_tag(test_repo, shas[2], "foo-2")  # Should not match

    from utils.git import get_matching_tag_commits
    result = get_matching_tag_commits(str(test_repo), "rel-*")

    assert isinstance(result, dict)
    assert len(result) == 1
    assert shas[1] in result
    assert result[shas[1]] == "rel-1"


def test_get_topo_ordered_commits(test_repo: Path):
    from utils.git import get_topo_ordered_commits
    topo = get_topo_ordered_commits(str(test_repo))
    assert isinstance(topo, list)
    assert len(topo) >= 3
    assert topo == get_log_shas(test_repo)


def test_is_ancestor(test_repo: Path):
    from utils.git import is_ancestor
    shas = get_log_shas(test_repo)
    assert is_ancestor(shas[0], shas[2], str(test_repo)) is True
    assert is_ancestor(shas[2], shas[0], str(test_repo)) is False


def test_parse_describe_output():
    from utils.git import parse_describe_output
    assert parse_describe_output("v1.2.3-4-gabcdef0") == ("v1.2.3", 4)
    assert parse_describe_output("rel-2-5-7-1-gabc1234") == ("rel-2-5-7", 1)
    assert parse_describe_output("v1.2.3") is None
