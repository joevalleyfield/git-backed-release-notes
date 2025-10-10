# Phase E Follow-On — Linting Depth & Quality Automation

## Why this matters
- Stricter linting and type checks surface issues earlier and keep the codebase consistent as contributors rotate in.
- Behave/tag hygiene prevents UI regressions from sneaking in untested paths.
- Pre-commit automation shortens feedback loops and aligns local vs CI expectations.

## Workstreams

### 1. Static analysis expansion
- Promote `ruff` to required in CI, enabling formatter, import sorting, and select rule sets (e.g., `B`, `C4`, `I`).
- Introduce type checking (`mypy` or `pyright`) for the hottest modules; document ignore strategy for legacy gaps.
- Capture lint/type outputs as artifacts so reviewers can spot noisy warnings.

### 2. Behave/tag enforcement
- Define allowed tag taxonomy (`@smoke`, `@javascript`, etc.) and add a script that fails on unknown tags.
- Guard against untagged Playwright steps by scanning `features/` during CI.
- Optionally, generate a lint report summarizing tag coverage per suite.

### 3. Developer workflow polish
- Provide a shared `pre-commit` configuration running `ruff`, formatters, and type checks.
- Document `uv run` helpers and add CI guard to ensure hooks stay in sync (`pre-commit.ci` or manual check).
- Offer remediation docs in `CONTRIBUTING.md` (fix commands, autofix guidance, how to update baselines).

## Dependencies & risks
- Type checking may require targeted `# type: ignore` silencing until annotations land; manage debt carefully.
- Stricter lint may flag legacy modules; stagger enforcement to avoid blocking urgent fixes.
- Pre-commit adoption depends on contributors installing hooks; include guard rails in CI.

## Acceptance signals
- CI fails on lint/type regressions unless consciously suppressed.
- Behave lint job enforces tag taxonomy and reports coverage metrics.
- Pre-commit hooks run clean for contributors and match the CI configuration.

## References
- Root plan: `issues/open/bootstrap-ci-with-pyproject.md`
- Current CI workflow: `.github/workflows/ci.yml`
