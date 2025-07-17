# Edit Release Field on Commit Page

Users can now edit the `release` field directly from the commit detail page.

## Implemented Behavior

- The commit page displays an input field populated with the current `release` value
- Users can submit changes via a POST form to `/commit/<sha>/update`
- The server updates the in-memory DataFrame and writes the change to the `.xlsx` file
- The spreadsheet is updated using an atomic write (temp file + replace)
- If no spreadsheet is loaded, the server responds with a 500 error
- If the commit SHA is not found in the spreadsheet, the server responds with a 404
- Only the submitted field is modified; unrelated fields are preserved
- Edits are verified via BDD tests, including persistence to disk

## Motivation

The `release` field identifies which release a commit contributes to.
Enabling inline editing simplifies post-hoc tagging and refinement
without editing the spreadsheet directly.

## Future Extensions

- Add dropdowns or autocompletion based on known releases
- Support editing from the index view
- Add undo or change history
- Respect file locking or open status from Excel or other tools

## Comments

### 2025.07.17.Th

Updated language to reflect implemented behavior. Mirrors the structure
and approach used for `issue` field editing.
