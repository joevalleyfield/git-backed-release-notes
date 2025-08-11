# 📎 Feature: Inline Editing on Index

```yaml
tags: [commit-editing, index-view, inline-editing]
status: open
```

## Goal

Allow users to edit the `release` and `issue` fields directly from the commit index view, without navigating to the commit detail page.

## Behavior

- [x] Fields appear editable (via `<input>` elements)
- [x] Changes may be submitted:
  - [x] On pressing Enter
  - [x] On blur
  ~- [ ] Via explicit Save/Cancel buttons (optional)~
- [x] Submissions update the metadata store, creating rows if necessary
- [x] Feature-tested for spreadsheet and non-spreadsheet modes
- [x] Supports `next` parameter to enable redirect after update
- [x] Optimistic UI updates (value updates immediately before round-trip)
- [x] Visually indicate:
  - [x] Unsaved changes
  - [x] Recently saved changes (for 1 sec)
- [x] Restore focus to edited field after save (if possible)

## Rationale

- Enables rapid metadata entry and correction
- Reduces context switching between index and detail views
- Makes batch editing practical
