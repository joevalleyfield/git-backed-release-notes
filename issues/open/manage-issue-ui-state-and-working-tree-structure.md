# Manage Issue Working Trees and Metadata from Web UI

Extend the Git Viewer to support managing issue state directly through the web interface, rather than requiring manual coordination between Git working trees and issue files.

## Goals

- Represent each issue (`issue_slug`) as a combination of:
  - A tracked Markdown file (metadata, status, etc.)
  - An optional working tree rooted on an intent commit
- Allow the user to create and associate intent commits directly from the web UI
- Support no-ff merges from issue working trees into implementation branches
- Keep the main repo history readable, meaningful, and traceable to intent

## Proposed Behavior

### Issue Index View

- Display all issues (open or closed) from a configured issue directory
- Show their status, associated commits (if any), and optionally edit them

### Commit Index View

- Display the `issue` slug for each commit (if present in spreadsheet)
- Link to the issue file (Markdown)
- Optionally, allow associating a commit with an issue directly

### Issue Detail View

- Render the Markdown from the issue file
- Show the current status and associated commits
- Provide controls to:
  - Create an intent commit
  - Create or link a working tree
  - Stage a no-ff merge to a target commit

## Configuration Options

--issues-dir=/path/to/issues

This directory can contain:

- open/ and closed/ for Markdown issue files
- Optionally: a directory per issue slug (e.g. /path/to/issues/foo-bar) that is a Git working tree

## Example Structure

 issues/
 ├── open/
 │   └── foo-bar.md
 ├── closed/
 │   └── unexpected-precedes.md
 ├── foo-bar/        # .git working tree with intent commit
 └── remove-self-following-tags/  # resolved issue tree

## Benefits

- Declarative and navigable issue structure
- No need to manually coordinate merges or ref management
- Fully auditable history of both intent and implementation
- Scales to multi-user or automation use cases

## Related Features

- `display-issue-slugs-in-index.md`
