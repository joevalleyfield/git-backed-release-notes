import subprocess
from pathlib import Path

from git_release_notes.utils.git import get_commit_parents_and_children
from tests.helpers.git_fixtures import create_tag


def test_get_describe_name_returns_expected_string(test_repo: Path):
    from git_release_notes.utils.git import get_describe_name

    shas = get_log_shas(test_repo)
    create_tag(test_repo, shas[0], "rel-0.1")

    # Middle commit should describe as rel-0.1-1-g...
    name = get_describe_name(str(test_repo), shas[1])
    assert name.startswith("rel-0.1-1-g")

    # Tagged commit should describe as rel-0.1
    name_direct = get_describe_name(str(test_repo), shas[0])
    assert name_direct == "rel-0.1"

    # No match case
    name_none = get_describe_name(str(test_repo), shas[2], match="nope-*")
    assert name_none is None


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
    sha0, sha1, sha2 = shas

    # SHA1 is child of SHA0
    parents, children = get_commit_parents_and_children(sha1, str(test_repo))
    assert parents == [sha0]
    assert sha2 in children

    # SHA0 is root, has no parents
    parents0, children0 = get_commit_parents_and_children(sha0, str(test_repo))
    assert parents0 == []
    assert sha1 in children0
