# Edit Release Field on Commit Page

Allow users to edit the `release` field directly from the commit detail page.

## Expected Behavior

- On the commit detail page, display an input field for the `release` value
- Submit updates via a POST form to an existing route (e.g., `/commit/<sha>/update`)
- Changes should persist to the underlying `.xlsx` file using an atomic write
- After submission, redirect back to the same commit page

## Motivation

The `release` field identifies which release a commit contributes to.
Enabling inline editing simplifies the process of tagging commits after
browsing their contents or grouping them into milestones.

This complements the existing ability to edit the `issue` field.

## Future Extensions

- Add dropdowns or autocompletion based on known releases
- Support editing from the index view
- Validate or normalize release values before saving
- Add support for editing multiple metadata fields at once
