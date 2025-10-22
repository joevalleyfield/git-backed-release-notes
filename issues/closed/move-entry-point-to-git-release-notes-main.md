# 📦 Task: Establish Package Entry Point in `git_release_notes/__main__.py`

```yaml
tags: [cli, packaging, bundler-prereq]
status: closed
closed: 2025-10-02
```

Relocated the CLI bootstrap into a proper package module as part of migrating the
project toward a modern Python package layout.

## Prior Layout

```
.
├── app.py
├── handlers/
├── utils/
├── templates/
├── features/
├── tests/
└── issues/
```

- No `pyproject.toml` or console script existed yet.
- Entry point lived in the top-level `app.py` script.
- Library code sat in flat `handlers/` and `utils/` directories.

## Migrated Layout

```
.
├── pyproject.toml
├── src/
│   └── git_release_notes/
│       ├── __init__.py
│       ├── __main__.py       # packaged CLI entry point
│       ├── handlers/
│       ├── utils/
│       ├── templates/
│       └── ...
└── tests/
```

- `pyproject.toml` defines packaging metadata and a console script.
- CLI entry point now lives in `git_release_notes/__main__.py` with `app.py` as a thin shim.
- Library code resides under the package namespace, aligning with bundler needs.

## Highlights

1. Created the `src/git_release_notes/` package skeleton with `__init__.py` files.
2. Relocated handler, utility, and template modules under the package namespace.
3. Added `git_release_notes/__main__.py` to expose the Tornado CLI bootstrap via `main()`.
4. Reduced `app.py` to a compatibility shim for existing workflows.
5. Authored `pyproject.toml` with metadata, dependencies, and a console entry.
6. Updated pytest, Behave, and supporting fixtures to import from the new package.
7. Rewrote README guidance to favor `python -m git_release_notes` and the console script.

## Definition of Done

- Confirmed that `python -m git_release_notes` launches the CLI.
- Built the package via `python -m build` using the new `pyproject.toml` (outside the sandbox).
- Retained `app.py` as a thin shim for backwards compatibility.
- Ran pytest and Behave against the packaged layout.

## Follow-on Work

- Required prerequisite for `issues/open/create-monolith-bundler.md`
- Enables bundler to treat `src/git_release_notes` as the authoritative source tree
- Opens the door for wheel/zipapp distribution and cleaner dependency management

## Postscript

2025-10-22: remove stray update-foo.sh script
