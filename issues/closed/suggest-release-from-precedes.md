# 📎 Feature: Suggest Release from Precedes Tag

```yaml
tags: [commit-editing, heuristics, detail-view, index-view]
status: closed
```

## Goal

When a commit lacks an assigned `release`, suggest one based on its `Precedes:` tag relationship.

## Behavior

- We now reuse the existing suggestion panel patterns from the commit detail page and index table:
  - The hint only surfaces when the stored `release` field is empty.
  - The hint renders in the same UI slot used by issue suggestions so the “Use” button, styling, and provenance badge stay consistent.
- We resolve the `Precedes:` tag to a known release name using the same metadata loader used by release editing and display the resolved value with a `Precedes` source badge.
- A one-click “Use” action fills the form input without overwriting existing values unless the user confirms.
- The hint stays hidden on commits whose `Precedes:` tag cannot be mapped to a known release.

## Rationale

- `Precedes:` is typically inferred from tag distance and is often the intended release
- This enables efficient triage of uncategorized commits
- Suggestion logic mirrors that used for issue slugs and can be unified

## Implementation Notes

- Introduced a `compute_release_suggestion()` helper (`git_release_notes.utils.release_suggestions`) that prefers a direct release tag on the commit before falling back to `Precedes` and mirrors the issue suggestion flow.
- Extended `handlers/commit.py` and `handlers/main.py` to sanitize spreadsheet metadata, compute release hints, and pass `release_suggestion` context into the templates.
- Updated the commit detail and index templates to surface release hints with matching UI affordances and “Use” actions.
- Added unit coverage in `tests/unit/test_release_suggestions.py` plus a Behave scenario (`features/commit_release_suggestion.feature`) and step assertions to validate the new hint end to end.
