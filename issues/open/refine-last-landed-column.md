# Issue: Improve “Last Landed” Accuracy

## Summary

Ensure the issue index’s “Last Landed” column reflects the latest landing commit that the issue detail view can surface. Bring the heuristic associations (metadata links, message mentions, touched paths) into the index pipeline and persist the results through the commit metadata store so the column stays populated across sessions.

## Acceptance Criteria

- Issues that surface commits on their detail page also show a non-blank “Last Landed” value when those commits exist.
- The derived landing timestamp survives server restarts for both CSV and spreadsheet-backed metadata stores.
- Fresh commits that relate to an issue update the index view without manual edits.

## Notes

- Both metadata backends expose pandas DataFrames; updates should work for each.
- Consider TTLs or commit-set hashes to decide when to refresh cached timestamps.
- Keep behavior aligned between issue detail and index views so they remain consistent.
