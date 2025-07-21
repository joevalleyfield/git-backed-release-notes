# Enable File-Based Editing in No-Spreadsheet Mode

This change enabled Markdown-backed editing and commit-to-issue linking when no spreadsheet is configured. It supports dogfooding workflows without relying on spreadsheet-based metadata.

## Summary of Outcomes

- Users can edit issue content via a Markdown-backed interface
- Commit-to-issue links are stored in a metadata CSV instead of the spreadsheet
- The UI and backing handlers work in both spreadsheet and file-backed modes
- Changes are persisted to disk and reflected immediately in the UI

## Implemented Features

- Editing issue Markdown content through the UI
- Saving changes via POST to `/issue/<slug>/update`
- Displaying linked commits on issue pages
- Persisting commit-to-issue links in a `.git-view-metadata/` CSV file
- Tests verifying behavior in file-backed (no-spreadsheet) mode

## Implementation Notes

- Markdown is stored under `issues/open/` and `issues/closed/`
- POST routes safely write edited content back to disk
- The app uses an injected `issues_dir` from `app.settings`
- No assumptions are made about structured fields (`status:`, etc.) yet

## Future Enhancements

- Field-level editing of structured metadata (`status`, `precedes`, etc.)
- Inline metadata or front-matter parsing if needed
- Unlinking commits or richer bi-directional views

## Related Issues

- `issues/open/manage-issue-ui-state-and-working-tree-structure.md` ← may be partially completed by this work
- `issues/closed/dogfooding-no-spreadsheet-mode.md`
- `issues/closed/edit-issue-field-on-commit-page.md`
- `issues/closed/display-issue-slugs-in-index.md`

