# Display Issue Slugs in Index View

Some commits are linked to project issues via the `issue` column in the spreadsheet.
This field currently exists in the data but is not rendered in the commit index table.

## Expected Behavior

- Show the `issue` column in the index table
- If the value is non-empty, display the slug
- ~~Optionally, link the slug to `issues/open/<slug>.md` or `issues/closed/<slug>.md` if desired~~

## Motivation

This will make it easier to track:

- What commits are associated with which issues
- Which issues have corresponding changes
- Which issues are still open or resolved

## Related Ideas

- Filter by issue slug
- Group commits by issue
- Add links to issue files or external issue trackers
