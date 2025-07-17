# 🌀 Git Viewer MVP

This is a minimal Tornado-based web viewer for navigating and annotating the commit history of a Git repository. It supports release documentation workflows by combining Git metadata with user-supplied annotations from a spreadsheet — now with editable fields and write-back support.

## ✨ Features

* Loads commit metadata from an Excel `.xlsx` file (one row per commit)
* Displays an interactive HTML table of commits, including:
  * Commit SHA (linked to detailed view)
  * Message, release labels, issue slugs, author date, and more
* Per-commit detail view shows:
  * `git show` output
  * Nearest matching tags: `Follows:` (before) and `Precedes:` (after)
  * Edit fields for `issue` and `release`, saved back to the spreadsheet
* Edits persist immediately using atomic overwrite
* Graph-aware tag navigation using `git describe` and `rev-list`
* Optional tag filtering via glob pattern (e.g., `rel-*`)
* Accepts CLI paths to both Git repository and spreadsheet
* Read-only mode when no spreadsheet is provided

## 🚀 Usage

```bash
python app.py --repo path/to/repo --excel-path path/to/commits.xlsx --tag-pattern "rel-*"
```

Then open [http://localhost:8888](http://localhost:8888) in your browser.

You can also omit `--excel-path` to run in read-only mode with Git metadata only:

```bash
python app.py --repo path/to/repo
```

### 🔧 Editing Metadata

The per-commit page allows editing the `issue` and `release` fields.
Edits are applied to the in-memory model and saved back to the spreadsheet on disk.
Conflicts (e.g. missing spreadsheet or unknown commit) result in clear error messages.

### 🔍 Debug Logging

This tool includes optional debug logging to aid in understanding how `Precedes:` and `Follows:` tags are resolved.

To enable:

```bash
python app.py commits.xlsx --repo path/to/repo --debug
```

Logged details include:

* Matching tags and their resolved commit SHAs
* The full traversal order of commits
* `git merge-base` ancestry checks for `Precedes:` candidates

The logger is scoped to the application and avoids affecting global logging configuration.

Logs go to stdout and can be redirected:

```bash
python app.py ... --debug > debug.log 2>&1
```

## 📦 Dependencies

* Python 3.8+
* `pandas`
* `openpyxl`
* `tornado`
