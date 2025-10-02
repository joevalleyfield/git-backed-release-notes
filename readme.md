# 🌀 Git Viewer MVP

This is a minimal Tornado-based web viewer for navigating and annotating the commit history of a Git repository. It supports release documentation workflows by combining Git metadata with user-supplied annotations from a spreadsheet — now with editable fields and write-back support.

## ✨ Features

* Loads commit metadata from an Excel `.xlsx` file (one row per commit)
* Displays an interactive HTML table of commits, including:
  * Commit SHA (linked to detailed view)
  * Message, release labels, issue slugs, author date, and more
* Per-commit detail view shows:
  * `git show` output (plain fallback with dynamic Diff2Html enhancement)
  * Nearest matching tags: `Follows:` (before) and `Precedes:` (after)
  * Edit fields for `issue` and `release`, saved back to the spreadsheet
* Fully styled interface with Bootstrap 5 and semantic HTML
* Edits persist immediately using atomic overwrite
* Inline editing model:  
  * Enter or blur saves immediately  
  * Escape cancels while still editing  
  * No Save/Cancel buttons (low-friction, spreadsheet-like experience)  
* Graph-aware tag navigation using `git describe` and `rev-list`
* Optional tag filtering via glob pattern (e.g., `rel-*`)
* Accepts CLI paths to both Git repository and spreadsheet
* Read-only mode when no spreadsheet is provided

## 🚀 Usage

```bash
python -m git_release_notes --repo path/to/repo \
    --excel-path path/to/commits.xlsx --tag-pattern "rel-*"
```

After installation (e.g. `pip install .`), you can also use the console entry:

```bash
git-release-notes --repo path/to/repo
```

Then open [http://localhost:8000](http://localhost:8000) in your browser.

You can omit `--excel-path` to run in read-only mode with Git metadata only:

```bash
python -m git_release_notes --repo path/to/repo
```

### Metadata and Issue Content

The per-commit page allows editing the `issue` and `release` fields.
Edits are applied to the in-memory model and saved back to disk.
Conflicts (e.g. missing spreadsheet or unknown commit) result in clear error messages.

This app supports two modes for metadata storage:

1. **With spreadsheet** (`git-view.metadata.xlsx`):
   - Commit metadata fields like `issue` and `release` are stored in the spreadsheet
   - Issue files (`issues/{open,closed}/*.md`) would be used if present, but typically aren't
   - Editing issue content is not supported in this mode

2. **Without spreadsheet**:
   - Commit metadata is stored in a CSV file generated on disk
   - Issue files (`issues/{open,closed}/*.md`) are used to display and edit issue content
   - Each commit’s `issue` field links to a corresponding Markdown file if present

### 🔍 Debug Logging

This tool includes optional debug logging to aid in understanding how `Precedes:` and `Follows:` tags are resolved.

To enable:

```bash
python -m git_release_notes --excel-path commits.xlsx --repo path/to/repo --debug
```

Logged details include:

* Matching tags and their resolved commit SHAs
* The full traversal order of commits
* `git merge-base` ancestry checks for `Precedes:` candidates

The logger is scoped to the application and avoids affecting global logging configuration.

Logs go to stdout and can be redirected:

```bash
python -m git_release_notes ... --debug > debug.log 2>&1
```

## 📦 Dependencies

* Python 3.8+
* `pandas`
* `openpyxl`
* `tornado`
