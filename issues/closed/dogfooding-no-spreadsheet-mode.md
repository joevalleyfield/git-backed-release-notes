# Dogfooding: No-Spreadsheet Mode

Support using the app without providing a spreadsheet — useful for dogfooding against repos like this one that already contain metadata (e.g., `issues/`, `tags`, commit messages).

## Goal

Allow `python app.py` (with no arguments) to run the app using only the Git repo in the current working directory.

## Tasks

* [X] Draft feature spec for no-spreadsheet mode
* [X] Implement fallback behavior when no `.xlsx` is provided
* [X] Traverse the Git repo and synthesize commit metadata in memory
* [X] Display index and commit detail pages as usual, even without spreadsheet
* ~~[ ] Gracefully skip features like tagging or issue linking that depend on spreadsheet~~
* [X] Write end-to-end test(s) for no-spreadsheet mode
* [X] Validate `python app.py` runs successfully with only a repo

## Notes

This represents a shift from the original MVP flow. Rather than requiring a spreadsheet to be authored first, this enables real-time inspection and progressive enhancement of a real repo, including this one.

---

## Comments

2025.07.16.We

✅ **Closing this issue** after manually verifying the commit page works in no-spreadsheet mode. We’ll track remaining enhancements and coverage else where.
