"""
Helpers for deriving release suggestions from commit context.

Mirrors the issue suggestion flow so handlers can surface a unified
hint UI when a commit lacks an explicit release value.
"""

from dataclasses import dataclass
from types import SimpleNamespace
from typing import Optional

from .git import find_precedes_tag, get_matching_tag_commits


@dataclass(frozen=True)
class ReleaseSuggestionResult:
    """Container describing inferred release suggestions for a commit."""

    suggestion: Optional[str]
    suggestion_source: Optional[str]
    precedes: Optional[SimpleNamespace] = None

    def as_dict(self) -> dict:
        """Return a dict representation for template contexts."""
        return {
            "release_suggestion": self.suggestion,
            "release_suggestion_source": self.suggestion_source,
        }


def compute_release_suggestion(
    repo_path: str,
    sha: str,
    *,
    current_release: str = "",
    precedes: Optional[SimpleNamespace] = None,
    tag_pattern: str = "rel-*",
) -> ReleaseSuggestionResult:
    """
    Compute a release suggestion using the commit's tag context.

    Args:
        repo_path: Filesystem path to the Git repository.
        sha: Commit SHA under consideration.
        current_release: Existing release metadata (empty string if unset).
        precedes: Optional pre-resolved Precedes namespace to reuse.
        tag_pattern: Glob for matching release tags (defaults to 'rel-*').

    Returns:
        ReleaseSuggestionResult with suggestion string and provenance source.
    """

    existing = (current_release or "").strip()
    if existing:
        return ReleaseSuggestionResult(suggestion=None, suggestion_source=None, precedes=precedes)

    if not sha:
        return ReleaseSuggestionResult(suggestion=None, suggestion_source=None, precedes=None)

    tag_map = get_matching_tag_commits(repo_path, tag_pattern)
    direct_tag = (tag_map.get(sha) or "").strip()
    if direct_tag:
        return ReleaseSuggestionResult(
            suggestion=direct_tag,
            suggestion_source="tag",
            precedes=precedes,
        )

    resolved_precedes = precedes or find_precedes_tag(sha, repo_path, tag_pattern)
    if resolved_precedes is None:
        return ReleaseSuggestionResult(suggestion=None, suggestion_source=None, precedes=None)

    suggestion = (resolved_precedes.base_tag or "").strip()
    if not suggestion:
        return ReleaseSuggestionResult(suggestion=None, suggestion_source=None, precedes=resolved_precedes)

    return ReleaseSuggestionResult(
        suggestion=suggestion,
        suggestion_source="precedes",
        precedes=resolved_precedes,
    )
