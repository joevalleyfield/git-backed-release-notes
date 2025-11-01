# Issue: Improved “Last Landed” Accuracy

## Summary

Adjusted the issue index so the “Last Landed” column now reflects the freshest landing commit used on the detail page. The pipeline infers commits via metadata, message mentions, and touched paths, persists the results through the metadata store, and surfaces the latest author timestamp across app restarts.

## Outcome

- Issues that show commits on their detail page now display a timestamp instead of an em dash in the index.
- The derived landing timestamp survives server restarts for both CSV- and spreadsheet-backed metadata stores.
- Newly related commits update the index automatically without manual edits.

## Notes

- Both metadata backends received matching updates since they share the same pandas-based store.
- We considered TTLs for the cached commit associations; current logic refreshes when new commits are inferred.
