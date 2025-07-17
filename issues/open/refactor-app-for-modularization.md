# Refactor: Modularization of Git Viewer App

## Motivation

The Git Viewer app was originally implemented in a single Python file (`app.py`). This made it easy to deploy and iterate on, but as the project grew, several drawbacks emerged:

- Difficult to test handlers and logic in isolation
- Harder to navigate and understand distinct responsibilities
- Not reusable for other projects or downstream tools
- Painful to reassemble the full app in a controlled way

## Goals

- Move request handlers into a `handlers/` directory
- Move Git/spreadsheet utilities into `utils/`
- Retain a simple `app.py` as the entrypoint and composition root
- Preserve the ability to reassemble a mono-script for downstream inclusion

## Directory Layout

The target modular layout looks like this:

    git_viewer/
    ├── app.py
    ├── handlers/
    │   ├── main.py
    │   ├── commit.py
    │   └── update.py
    ├── utils/
    │   ├── git.py
    │   └── data.py
    ├── templates/
    │   ├── index.html
    │   └── commit.html

## Component Mapping

Handlers:

- `MainHandler` → `handlers/main.py`
- `CommitHandler` → `handlers/commit.py`
- `UpdateCommitHandler` → `handlers/update.py`

Utility functions:

- `extract_commits_from_git()` → `utils/git.py`
- `get_row_index_by_sha()`, `atomic_save_excel()` → `utils/data.py`

## Mono-Include Strategy

To preserve the ability to ship a single-file version of the app (for downstream use or simplicity), we can generate a stitched-together file using a tool like this:

    # tools/bundle.py
    from pathlib import Path

    ORDER = [
        "utils/data.py",
        "utils/git.py",
        "handlers/main.py",
        "handlers/commit.py",
        "handlers/update.py",
        "app.py",
    ]

    with open("git_viewer_monolith.py", "w") as out:
        for file in ORDER:
            out.write(f"# === {file} ===\\n")
            out.write(Path(file).read_text())
            out.write("\\n\\n")

This keeps the modular dev layout while preserving portability.

## Future Work

- Add unit tests for `utils/git.py` and `utils/data.py`
- Consider Jinja2 templating
- Investigate `pex` or `shiv` for bundling as a zipapp
- Add `__init__.py` files to support future import as a library
