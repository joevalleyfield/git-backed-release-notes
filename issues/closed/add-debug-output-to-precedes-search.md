# Add Debug Output to Precedes Tag Lookup

To help diagnose missing `Precedes:` tags, add optional debug output to
`find_precedes_tag()` to show:

- Whether each tag matches the pattern
- Whether `merge-base` returns true for each tag candidate
- Which tags are skipped and why

This was used to assist in understanding false negatives in tag lookup logic.

## Approach

- Add a `--debug` CLI flag to enable verbose logging

## Possible Follow-on

- Print diagnostics to stderr or structured log
