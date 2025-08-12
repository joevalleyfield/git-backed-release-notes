# Inline Edit Release and Issue

Allowed users to edit the `release` and `issue` fields directly from the commit index page.

## Behavior

- [x] Fields appeared editable (via `<input>` elements)
- [x] Changes could be submitted:
  - [x] On pressing Enter
  - [x] On blur
  ~- [ ] Via explicit Save/Cancel buttons (optional)~
- [x] Submissions updated the metadata store, creating rows if necessary
- [x] Feature-tested for spreadsheet and non-spreadsheet modes
- [x] Supported `next` parameter to enable redirect after update
- [x] Provided optimistic UI updates (value updated immediately before round-trip)
- [x] Visually indicated:
  - [x] Unsaved changes
  - [x] Recently saved changes (for 1 sec)
- [x] Restored focus to edited field after save (if possible)

## Rationale

This feature streamlined commit metadata editing by enabling quick, inline updates without navigating to the commit detail view. Users could make edits in place with immediate feedback and minimal disruption to workflow.
