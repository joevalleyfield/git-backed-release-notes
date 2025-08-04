# 📎 Feature: Suggest Primary Issue on Commit Detail Page

```yaml
tags: [commit-editing, heuristics, detail-view]
status: open
```

## Goal

Suggest the most likely primary issue slug when editing a commit on its detail page.

## Behavior

- Use `extract_issue_slugs()` to identify the top directive-based issue
- Present it just above or inside the editable `issue` field
- Display as:
  - A prefilled value
  - Or a hint with a “Use this” button
- Should not overwrite existing values unless user confirms

## Rationale

- Reduces friction for single-issue tagging
- Makes parsing logic visible and trustable
- Avoids manual copy/paste from commit message
