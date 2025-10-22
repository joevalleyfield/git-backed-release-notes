# 📎 Feature: Show Suggested Issues on Index View

```yaml
tags: [commit-editing, heuristics, index-view]
status: open
```

## Goal

Display suggested issue slugs next to commits in the index view using the same heuristics as the commit detail page.

## Behavior

- For each commit, extract candidate issue slugs using `extract_issue_slugs()`
- Display the top match alongside the issue field as a linked hint with a one-click "Use" action
- Skip rendering a hint when the stored issue already matches the suggestion

## Rationale

- Helps users spot and apply likely issue links without leaving the index
- Reduces need to copy/paste from the commit message
- Aligns with behavior already available on commit detail page

## Implementation Notes
2025-10-22: consolidated directive/message/touched suggestions into a shared helper; index renders linked "Use" hint when metadata is empty
