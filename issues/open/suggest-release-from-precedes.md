# 📎 Feature: Suggest Release from Precedes Tag

```yaml
tags: [commit-editing, heuristics, detail-view, index-view]
status: open
```

## Goal

When a commit lacks an assigned `release`, suggest one based on its `Precedes:` tag relationship.

## Behavior

- On both the index and detail pages:
  - If `release` is missing
  - And a `Precedes:` tag is resolved
- Show a visual hint (e.g., “Suggested: rel-1.2”)
- Optionally offer a one-click “Apply” button to fill it in
- Should never overwrite existing values without confirmation

## Rationale

- `Precedes:` is typically inferred from tag distance and is often the intended release
- This enables efficient triage of uncategorized commits
- Suggestion logic mirrors that used for issue slugs and can be unified
