# Fix stale index in spreadsheet mode

## Summary

When running in spreadsheet-backed mode, the main page (`MainHandler`) was displaying a **stale copy** of commit metadata. The application was caching a DataFrame (`df`) in `application.settings`, and `MainHandler` rendered directly from that copy instead of consulting the metadata store.

As a result:

* Updates made through the application's own edit endpoint did **not** appear in the index table immediately.
* Tests that asserted the presence of issue slugs in the index were effectively validating the stale behavior rather than the intended live behavior.

## Steps to Reproduce

1. Start the server in spreadsheet-backed mode.
2. Load the index page – note that an issue slug from the spreadsheet is shown.
3. Use the app's edit functionality to change the issue or release for a commit.
4. Reload the index page.
5. **Observed:** Changes do not appear; old values are still shown.
6. **Expected:** Index should always reflect the current contents of the metadata store after an edit.

## Root Cause

* `MainHandler` was holding onto `self.df = application.settings["df"]`.
* The edit endpoint updated the store, but the handler never re-queried it, so the index stayed stale.

## Resolution

* Remove `df` from application settings.
* Add `get_metadata_df()` and `limits_commit_set()` to `CommitMetadataStore` API.
* Update `MainHandler` to always consult the store for rows, ensuring the index is in sync.
* Adjust tests: replace the old “stale index” assumption with scenarios that confirm issue slugs appear from the spreadsheet and that edits propagate to the index.

## Exit Criteria

* Index page in spreadsheet mode always reflects the latest values in the spreadsheet/store.
* Editing issue/release via UI updates the index without requiring a server restart.
* Feature tests confirm both spreadsheet slugs render initially and that edits are reflected.

## Findings

* Git commit `9944df6ca467` (“fix: make index page reflect updates in spreadsheet mode.”) removed the cached `df` from `MainHandler` and now rebuilds rows from `commit_metadata_store.get_metadata_df()` on every request, so inline edits show up immediately.
* `CommitMetadataStore` gained `get_metadata_df()` and `limits_commit_set()` so both spreadsheet- and CSV-backed stores surface fresh data to the handler.
* Behave coverage already exercises the index edit flow and asserts the updated slug is present in the HTML response, keeping this regression locked down.

## Postscript
2025-10-29: Verified the spreadsheet mode refresh via commit `9944df6ca467`; no additional work required.

## Tags
needs-testing
