# 📎 Feature: Suggest Release from Precedes Tag

```yaml
tags: [commit-editing, heuristics, detail-view, index-view]
status: open
```

## Goal

When a commit lacks an assigned `release`, suggest one based on its `Precedes:` tag relationship.

## Behavior

- Reuse the existing suggestion panel patterns from the commit detail page and index table:
  - Only surface the hint when the stored `release` field is empty.
  - Render the hint in the same UI slot used by issue suggestions so the “Use” button, styling, and provenance badge stay consistent.
- Resolve the `Precedes:` tag to a known release name using the same metadata loader used by release editing; show the resolved value plus a `Precedes` source label.
- Allow a one-click “Apply” action that fills the form input but never overwrites an existing value without confirmation.
- Keep the hint hidden on commits whose `Precedes:` tag cannot be mapped to a release we know about.

## Rationale

- `Precedes:` is typically inferred from tag distance and is often the intended release
- This enables efficient triage of uncategorized commits
- Suggestion logic mirrors that used for issue slugs and can be unified

## Implementation Notes

- Mirror the `compute_issue_suggestion()` flow in `git_release_notes.utils.issue_suggestions` with a dedicated helper (or parameterize the existing one) so the handlers receive a `ReleaseSuggestionResult` object with `.suggestion` and `.suggestion_source`.
- Both `handlers/commit.py` and `handlers/main.py` already know how to thread suggestion data into the templates; extend their context dictionaries with `release_suggestion` fields, following the same shape as the issue suggestion keys.
- The shared templates (`templates/commit.html`, `templates/index.html`) have reusable hint components—duplicate the markup only as needed to swap labels and `data-*` attributes.
- Add unit coverage alongside `tests/unit/test_issue_suggestions.py` (or a sibling file) that exercises commits with and without `Precedes:` tags, plus mismatched tags that should suppress the hint.
- Backfill a Behave scenario that confirms the detail page can apply the suggested release, mirroring the flows introduced in `suggest-primary-in-commit-detail.md` and `suggest-issues-on-index.md`.
