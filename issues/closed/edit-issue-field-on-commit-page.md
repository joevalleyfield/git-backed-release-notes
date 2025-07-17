# Edit Issue Field on Commit Page

Users can now edit the `issue` field directly from the commit detail page.

## Implemented Behavior

- The commit page displays an input field populated with the current `issue` value
- Users can submit changes via a POST form to `/commit/<sha>/update`
- The server updates the in-memory DataFrame and writes the change to the `.xlsx` file
- Changes are persisted immediately using an atomic write (temp file + replace)
- If no spreadsheet is loaded, the server responds with a 500 error
- If the commit SHA is not found in the spreadsheet, the server responds with a 404
- Edits are verified via BDD tests, including persistence to disk

## Motivation

This provides a low-friction way to associate commits with issues after reviewing them,
without needing to edit the spreadsheet manually.

## Future Extensions

- Add editing for `release` or `labels` fields
- Support inline editing from the index view
- Add undo or change history
- Respect locking or show file status if the `.xlsx` is open elsewhere
- Optionally delay persistence or debounce writes

## Comments

### 2025.07.17.Th

Updated language to past tense, reflecting implemented status and actual behavior.