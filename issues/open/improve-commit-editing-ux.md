# 📎 Task: Improve Commit Editing UX

```yaml
tags: [commit-editing, heuristics, ui]
status: open
```

Improve metadata editing across commit index and detail pages to support
faster, smarter, and more intuitive workflows for assigning `issue` and
`release` values.

## Behavior Tree

- **Root Goal**: Improve commit editing UX

  - [A] **Inline Editing on Index**
    Edit `issue` and `release` fields directly in the index list view  
    _(see: inline-edit-release-and-issue.md)_

  - [B] **Heuristic Suggestions on Index**
    Show suggested issue slugs inferred from commit messages  
    _(see: suggest-issues-on-index.md)_

  - [C] **Suggested Primary in Commit Detail**
    Surface top inferred issue slug as a click-to-adopt suggestion  
    _(see: suggest-primary-in-commit-detail.md)_

  - [D] **Suggested Release from Precedes**
    Use resolved `Precedes:` tag as default suggestion for `release`  
    _(see: suggest-release-from-precedes.md)
