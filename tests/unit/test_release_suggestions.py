from git_release_notes.utils.release_suggestions import (
    ReleaseSuggestionResult,
    compute_release_suggestion,
)
from tests.helpers.git_fixtures import create_tag, get_log_shas

pytest_plugins = ["tests.helpers.git_fixtures"]


def _seed_tags(repo, shas):
    create_tag(repo, shas[0], "rel-0.1")
    create_tag(repo, shas[2], "rel-0.2")


def test_suggests_release_from_precedes(test_repo):
    shas = get_log_shas(test_repo)
    _seed_tags(test_repo, shas)

    result = compute_release_suggestion(str(test_repo), shas[1], current_release="")

    assert isinstance(result, ReleaseSuggestionResult)
    assert result.suggestion == "rel-0.2"
    assert result.suggestion_source == "precedes"


def test_skips_when_release_already_present(test_repo):
    shas = get_log_shas(test_repo)
    _seed_tags(test_repo, shas)

    result = compute_release_suggestion(str(test_repo), shas[1], current_release="rel-0.1")

    assert result.suggestion is None
    assert result.suggestion_source is None


def test_prefers_direct_tag_over_precedes(test_repo):
    shas = get_log_shas(test_repo)
    create_tag(test_repo, shas[0], "rel-0.1")

    result = compute_release_suggestion(str(test_repo), shas[0], current_release="")

    assert isinstance(result, ReleaseSuggestionResult)
    assert result.suggestion == "rel-0.1"
    assert result.suggestion_source == "tag"


def test_returns_none_without_precedes_tag(test_repo):
    shas = get_log_shas(test_repo)

    result = compute_release_suggestion(str(test_repo), shas[1], current_release="")

    assert result.suggestion is None
    assert result.suggestion_source is None
