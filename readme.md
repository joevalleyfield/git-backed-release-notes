# 🌀 Git Viewer MVP

This is a minimal Tornado-based web viewer for navigating and annotating the commit history of a Git repository. It’s designed to support release documentation workflows by combining Git metadata with user-supplied annotations from a spreadsheet.

## ✨ Features

* Loads commit metadata from an Excel `.xlsx` file (one row per commit)
* Displays an interactive HTML table of commits with:

  * Commit SHA (linked to detailed view)
  * Message, release labels, author date, and more
* Detailed per-commit view includes:

  * `git show` output
  * Nearest matching tag before (`Follows:`) and after (`Precedes:`) the commit
  * Tag references are linkable and graph-aware (via `git describe` and `rev-list`)
* Supports filtering tags by glob pattern (e.g. `rel-*`)
* Accepts paths to both the spreadsheet and the Git repository via CLI

## 🚀 Usage

```bash
python app.py path/to/commits.xlsx --repo path/to/repo --tag-pattern "rel-*"
```

Then open [http://localhost:8888](http://localhost:8888) in your browser.

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

Logs go to stdout and can be redirected in the normal way:

```bash
python app.py ... --debug > debug.log 2>&1
```

## 📦 Dependencies

* Python 3.8+
* `pandas`
* `openpyxl`
* `tornado`
