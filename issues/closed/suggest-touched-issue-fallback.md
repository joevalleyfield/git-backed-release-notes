# 📎 Feature: Suggest Issue Fallback From Touched Files

```yaml
tags: [commit-editing, heuristics, detail-view]
status: open
```

## Goal

When a commit lacks directive-style issue references, fall back to the touched
issue files to suggest a likely primary slug on the commit detail page.

## Behavior

- Inspect the list of issue files (`issues/open/*.md`, `issues/closed/*.md`) touched
  in the commit diff.
- When `extract_issue_slugs()` produces no primary directive match and the commit
  metadata store does not already link an issue, promote the touched slug as a
  suggestion.
- Display the suggestion in the same UI affordance used for directive-driven
  hints, including "Use this suggestion" button behavior.
- Avoid suggesting slugs that already have an explicit directive match or are
  unrelated (e.g., non-issue files).

## Rationale

- Keeps the commit detail page helpful even when commit messages omit directives.
- Aligns the suggestion panel with the related-issues heuristic we already compute.
- Reduces manual copy/paste when a commit only touches a single issue file.

## Implementation Notes
2025-10-22: directive-first with touched-file fallback (change 15ad6b49)
