# Use anchor in `Back` link to scroll to commit row

When navigating from the index page to a commit detail view, the "Back" link should return the user to the same commit's row in the index. This can be accomplished by:

- Assigning an `id="sha-<short_sha>"` to each commit row or container on the index page
- Updating the "Back" link on the commit detail view to point to `/#sha-<short_sha>`

This would make it easier to resume work on neighboring commits after viewing or editing details for a specific one.
