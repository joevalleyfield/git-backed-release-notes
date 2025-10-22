# Fix: Issue page with spreadsheet-backed metadata store

## Problem
Issue page needed spreadsheet support hardening.
Originally the handler touched `.df` on the metadata store and failed when `SpreadsheetCommitMetadataStore` was active; that API has since been abstracted, but regression tests were missing.

## Proposed Fix
- Add `reload()` and `shas_for_issue(slug)` methods to the `CommitMetadataStore` ABC.
- Implement these in both `SpreadsheetCommitMetadataStore` and `DataFrameCommitMetadataStore`.
- Update `IssueDetailHandler.get` to use the abstracted API instead of accessing `.df`.

## Exit Criteria
- Issue page loads correctly whether metadata comes from CSV or spreadsheet.
- No direct references to `.df` in handlers.
- Tests show issue-to-commit linking works for both store types.

## Status
closed

## Tags
tested

## Notes
- 2025-10-22: Added unit coverage for `DataFrameCommitMetadataStore` and `SpreadsheetCommitMetadataStore` (`shas_for_issue`, `reload`) in `tests/unit/test_metadata_store.py`.
- 2025-10-22: Added `features/issue_spreadsheet_mode.feature` to exercise the issue detail page in spreadsheet mode and confirm linked commits render.
