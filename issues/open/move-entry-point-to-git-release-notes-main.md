# 📦 Task: Establish Package Entry Point in `git_release_notes/__main__.py`

```yaml
tags: [cli, packaging, bundler-prereq]
status: open
```

Relocate the CLI bootstrap into a proper package module as part of migrating the
project toward a modern Python package layout.

## Current State Snapshot

```
.
├── app.py                # delegating shim
├── src/git_release_notes/
│   ├── __init__.py
│   ├── __main__.py       # new CLI bootstrap
│   ├── handlers/
│   ├── templates/
│   └── utils/
├── features/
├── tests/
└── issues/
```

- No `pyproject.toml` packaging metadata yet
- CLI entry point now lives in `git_release_notes/__main__.py` (invoked via shim)
- Library code resides under the package namespace for bundler alignment

## Target Layout (canonical src layout)

```
.
├── pyproject.toml
├── src/
│   └── git_release_notes/
│       ├── __init__.py
│       ├── __main__.py       # new CLI bootstrap
│       ├── handlers/
│       ├── utils/
│       ├── templates/
│       └── ...
└── tests/
```

## Migration Plan

1. [x] Create `src/git_release_notes/` package skeleton with `__init__.py`
2. [x] Move reusable modules from `handlers/` and `utils/` under the new package
3. [x] Add `src/git_release_notes/__main__.py` that exposes the CLI entry point via `main()`
4. [x] Update `app.py` to import-and-delegate (or deprecate) while existing scripts migrate
5. [x] Introduce `pyproject.toml` defining the `git-release-notes` project and console entry
6. [x] Adjust imports, fixtures, and tests (pytest + Behave harness) to the new package paths and module invocation
7. [x] Update documentation (README) to invoke `python -m git_release_notes`; update CI scripts as a follow-up

## Definition of Done

- Running `python -m git_release_notes` launches the CLI
- The package builds via `python -m build` using the new `pyproject.toml`
- Old `app.py` path emits deprecation warning or is retained as thin shim
- Tests and automation succeed against the packaged layout

## Follow-on Work

- Required prerequisite for `issues/open/create-monolith-bundler.md`
- Enables bundler to treat `src/git_release_notes` as the authoritative source tree
- Opens the door for wheel/zipapp distribution and cleaner dependency management
