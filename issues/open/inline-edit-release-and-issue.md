# Support inline editing of release and issue fields on index view

Allow users to edit the `release` and `issue` fields directly from the index view, rather than navigating to the commit detail page.

This might be implemented as:

- Making the release and issue columns editable via `contenteditable`, `<input>`, or similar widgets
- Submitting changes via AJAX or form submission on blur or Enter
- Optionally indicating edited rows visually or showing save/undo buttons

Would greatly improve UX for quick batch editing.
