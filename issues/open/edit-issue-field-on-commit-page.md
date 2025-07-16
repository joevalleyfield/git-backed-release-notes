# Edit Issue Field on Commit Page

Allow users to edit the `issue` field directly from the commit detail page.

## Expected Behavior

- On the commit detail page, display an input field for the `issue` slug.
- Submit updates via a POST form to a new route (e.g., `/commit/<sha>/edit-issue`).
- Changes should persist to the underlying `.xlsx` file (or in-memory model).
- After submission, redirect back to the same commit page.

## Motivation

This provides a simple way to associate commits with issues after reviewing them,
without needing to open Excel or manipulate the spreadsheet manually.

It's a low-friction path toward refining commit metadata and can serve as a
proof-of-concept for future inline editing features.

## Future Extensions

- Add editing for `release` or `labels` fields
- Support editing in index view
- Add undo or change history
- Respect locking or show file status if the `.xlsx` is open elsewhere
