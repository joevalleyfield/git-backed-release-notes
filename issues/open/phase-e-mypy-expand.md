# Phase E Follow-On — Expand MyPy Coverage

## Why this matters
- Utilities are typed, but handlers, scripts, and Behave glue still run unchecked.
- Gradually widening MyPy’s scope catches interface drift and keeps refactors safe.

## Incremental plan
1. Annotate Tornado handlers (`src/git_release_notes/handlers/`) and add them to MyPy’s `files` list.
2. Bring `src/git_release_notes/__main__.py` and CLI scripts under MyPy once option parsing is typed.
3. Evaluate Behave step modules (`features/steps/`)—decide whether to stub them or keep them untyped.
4. Add tests and helper packages (`tests/`, `scripts/`) as feasible, documenting the ignore strategy.

## Risks / blockers
- Tornado’s dynamic request handler API may need stubs or `# type: ignore` during the migration.
- Behave fixtures rely on dynamic attributes; may require custom type definitions or be excluded.

## Acceptance signals
- `tool.mypy.files` covers handlers + CLI + scripts (beyond utils).
- CI reports zero MyPy errors across the expanded scope.
- Documentation updated to reflect the broader typed footprint.

## Status
- 2025-10-10: Baseline MyPy checks limited to `src/git_release_notes/utils`.

## References
- Parent plan: `issues/open/phase-e-expand-coverage.md`
- Current config: `pyproject.toml` (`[tool.mypy]` section)
