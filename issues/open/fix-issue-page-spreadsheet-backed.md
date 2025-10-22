# Fix: Issue page with spreadsheet-backed metadata store

## Problem
Visiting an issue page fails when the `SpreadsheetCommitMetadataStore` is in use.
The handler directly touches `.df` on the store, which is a private implementation detail.
As a result, associated commits are not found and the page does not load.

## Proposed Fix
- Add `reload()` and `shas_for_issue(slug)` methods to the `CommitMetadataStore` ABC.
- Implement these in both `SpreadsheetCommitMetadataStore` and `DataFrameCommitMetadataStore`.
- Update `IssueDetailHandler.get` to use the abstracted API instead of accessing `.df`.

## Exit Criteria
- Issue page loads correctly whether metadata comes from CSV or spreadsheet.
- No direct references to `.df` in handlers.
- Tests show issue-to-commit linking works for both store types.

## Status
open

## Tags
spiked, needs-tests

## Notes
- 2025-10-22: Added unit coverage for `DataFrameCommitMetadataStore` and `SpreadsheetCommitMetadataStore` (`shas_for_issue`, `reload`) in `tests/unit/test_metadata_store.py`.
- Still missing a Behave scenario that visits `/issue/<slug>` while the app runs in `@with_xlsx` mode to prove spreadsheet-backed issue views work end-to-end.
