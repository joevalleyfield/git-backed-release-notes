# 📎 Feature: Show Suggested Issues on Index View

```yaml
tags: [commit-editing, heuristics, index-view]
status: open
```

## Goal

Display suggested issue slugs next to commits in the index view using the same heuristics as the commit detail page.

## Behavior

- For each commit, extract candidate issue slugs using `extract_issue_slugs()`
- Display the top match (or all matches) in a lightweight visual form:
  - As a gray hint label (e.g., “Suggested: #foo-bar”)
  - As a prefilled but editable field
- May be linked to editing interaction (e.g., click-to-adopt)

## Rationale

- Helps users spot and apply likely issue links without leaving the index
- Reduces need to copy/paste from the commit message
- Aligns with behavior already available on commit detail page
