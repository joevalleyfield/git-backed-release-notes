from types import SimpleNamespace
from typing import Sequence

from .commit_parsing import extract_issue_slugs


def find_commits_referring_to_issue(slug: str, commits: Sequence[SimpleNamespace]) -> list[SimpleNamespace]:
    referring = []

    for row in commits:
        # Check 1: explicitly annotated issue (if available)
        if getattr(row, "issue", None) == slug:
            referring.append(row)
            continue

        # Check 2: directive or mention in message
        _, linked = extract_issue_slugs(row.message)
        if slug in linked:
            referring.append(row)
            continue

        # Check 3: touched paths
        paths = getattr(row, "touched_paths", []) or []
        if f"issues/open/{slug}.md" in paths or f"issues/closed/{slug}.md" in paths:
            referring.append(row)

    return referring
