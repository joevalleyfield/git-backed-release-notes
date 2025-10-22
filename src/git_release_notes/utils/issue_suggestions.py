# utils/issue_suggestions.py

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

from .commit_parsing import extract_issue_slugs


@dataclass
class IssueSuggestionResult:
    """Container describing inferred issue suggestions for a commit."""

    existing_issues: list[str]
    directive_primary: Optional[str]
    message_matches: list[str]
    touched_issue_slugs: list[str]
    suggestion: Optional[str]
    suggestion_source: Optional[str]

    def for_render(self) -> dict[str, Optional[str] | list[str]]:
        """Return a dict of the key render-friendly attributes."""
        return {
            "existing_issues": self.existing_issues,
            "issue_suggestion": self.suggestion,
            "issue_suggestion_source": self.suggestion_source,
        }


def compute_issue_suggestion(
    repo_path: Path | str,
    message_text: str,
    *,
    touched_paths: Iterable[str] | None = None,
) -> IssueSuggestionResult:
    """
    Compute directive-derived and touched-file-based issue suggestions for a commit.

    Args:
        repo_path: Root of the Git repository that contains `issues/open` and `issues/closed`.
        message_text: Commit message (or git show header) to scan for directive slugs.
        touched_paths: Optional iterable of paths touched by the commit (relative to repo root).

    Returns:
        IssueSuggestionResult capturing candidate slugs, suggestion choice, and provenance.
    """

    repo_root = Path(repo_path)
    touched_paths_list = list(touched_paths or [])

    primary, slugs = extract_issue_slugs(message_text or "")
    message_matches: list[str] = []

    for slug in slugs:
        if _issue_exists(repo_root, slug):
            message_matches.append(slug)

    touched_issue_slugs: list[str] = []
    for path in touched_paths_list:
        if path.startswith("issues/open/") or path.startswith("issues/closed/"):
            if path.endswith(".md"):
                slug = Path(path).stem
                if slug not in touched_issue_slugs:
                    touched_issue_slugs.append(slug)

    existing_issues = _dedupe_preserving_order(message_matches + touched_issue_slugs)
    touched_candidates = [slug for slug in touched_issue_slugs if slug not in message_matches]

    suggestion: Optional[str] = None
    suggestion_source: Optional[str] = None

    if primary and primary in existing_issues:
        suggestion = primary
        suggestion_source = "directive"
    elif message_matches:
        suggestion = message_matches[0]
        suggestion_source = "message"
    elif touched_candidates:
        suggestion = touched_candidates[0]
        suggestion_source = "touched"

    return IssueSuggestionResult(
        existing_issues=existing_issues,
        directive_primary=primary,
        message_matches=message_matches,
        touched_issue_slugs=touched_candidates,
        suggestion=suggestion,
        suggestion_source=suggestion_source,
    )


def _issue_exists(repo_root: Path, slug: str) -> bool:
    for subdir in ("open", "closed"):
        issue_path = repo_root / "issues" / subdir / f"{slug}.md"
        if issue_path.exists():
            return True
    return False


def _dedupe_preserving_order(items: list[str]) -> list[str]:
    seen = set()
    deduped = []
    for item in items:
        if item not in seen:
            seen.add(item)
            deduped.append(item)
    return deduped
