# Enable File-Based Editing in No-Spreadsheet Mode

Implement Markdown-backed editing and commit-to-issue linking when no spreadsheet is configured. This enables dogfooding workflows without requiring spreadsheet-based metadata.

## Goals

- Allow editing of issue files (`.md`) directly from the UI in no-spreadsheet mode
- Enable associating commits with issues without relying on spreadsheet rows
- Keep changes reversible and traceable via version control (edits to issue files or metadata)

## 🔨 Task Checklist

- [ ] Detect and allow edits in no-spreadsheet mode
- [ ] Enable issue field editing (`status`, `title`, etc.)
- [ ] Write back Markdown file safely
- [ ] Add file-backed commit-to-issue metadata
- [ ] UI to link/unlink commit to issue
- [ ] Reflect changes live without spreadsheet reload
- [ ] Final smoke test in no-xlsx mode

## Proposed Behavior

### Issue Detail View

- Issue Markdown is editable (fields like `status`, `title`, `precedes`, etc.)
- Save button writes back to file in-place (or safely via temp file swap)
- Commits associated with this issue are displayed using one of:
  - Inline metadata in the Markdown file
  - A metadata directory (e.g. `.git-view-metadata/`)
  - Parsing of commit messages (e.g. `Resolves #slug`)

### Commit Detail View

- If no spreadsheet is present:
  - Commit's associated issue (if any) is inferred and shown
  - UI allows linking this commit to an issue (e.g. dropdown or slug field)
  - Association is stored in file-based metadata, not spreadsheet

## Implementation Notes

- Add safe file-writing logic for issue Markdown and/or `.git-view-metadata/`
- Consider a registry or format for storing commit-to-issue links:
  - `.git-view-metadata/commit-to-issue/<commit-hash>` → `slug`
  - or a single `commit-to-issue.json` file

## Stretch Goals

- Real-time preview of linked commits based on parsed messages
- Bi-directional linkage: show which commits mention a given issue slug
- Integration with intent-commit and working tree scaffolding (see below)

## Related Issues

- `issues/open/manage-issue-ui-state-and-working-tree-structure.md` ← may be partially completed by this work
- `issues/closed/dogfooding-no-spreadsheet-mode.md`
- `issues/closed/edit-issue-field-on-commit-page.md`
- `issues/closed/display-issue-slugs-in-index.md`
