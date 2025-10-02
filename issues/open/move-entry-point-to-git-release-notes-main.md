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
├── app.py
├── handlers/
├── utils/
├── templates/
├── features/
├── tests/
└── issues/
```

- No `pyproject.toml` packaging metadata
- Executable entry point lives in the top-level `app.py`
- Library code is split across `handlers/` and `utils/` without package namespaces

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

1. Create `src/git_release_notes/` package skeleton with `__init__.py`
2. Move reusable modules from `handlers/` and `utils/` under the new package
3. Add `src/git_release_notes/__main__.py` that exposes the CLI entry point via `main()`
4. Update `app.py` to import-and-delegate (or deprecate) while existing scripts migrate
5. Introduce `pyproject.toml` defining the `git-release-notes` project and console entry
6. Adjust imports, fixtures, and tests to the new package paths
7. Update documentation and CI scripts to invoke `python -m git_release_notes`

## Definition of Done

- Running `python -m git_release_notes` launches the CLI
- The package builds via `python -m build` using the new `pyproject.toml`
- Old `app.py` path emits deprecation warning or is retained as thin shim
- Tests and automation succeed against the packaged layout

## Follow-on Work

- Required prerequisite for `issues/open/create-monolith-bundler.md`
- Enables bundler to treat `src/git_release_notes` as the authoritative source tree
- Opens the door for wheel/zipapp distribution and cleaner dependency management
