# 📎 Feature: Inline Editing on Index

```yaml
tags: [commit-editing, index-view, inline-editing]
status: open
```

## Goal

Allow users to edit the `release` and `issue` fields directly from the commit index view, without navigating to the commit detail page.

## Behavior

- [x] Release and issue fields should appear editable (e.g., `contenteditable`, `<input>`, or `<textarea>`)
- [x] Changes may be submitted:
  - On blur
  - [x] On pressing Enter
  - Via explicit save/cancel buttons (optional)
- Optimistic UI updates are allowed
- [ ] Rows with unsaved or recently saved changes may be visually indicated
- [ ] Keyboard focus should be preserved after editing if possible

## Rationale

- Enables rapid metadata entry and correction
- Reduces context switching between index and detail views
- Makes batch editing practical
