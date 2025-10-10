    # 🚦 CI/CD Roadmap Grounded in `pyproject.toml`

    ## Why this plan
    - Anchor on the existing `pyproject.toml` that already defines metadata and dependency ranges.
    - Deliver usable CI/CD and onboarding paths quickly, then iterate toward stronger compliance (SBOM, dependency automation).
    - Reconcile earlier pinned-requirements ideas with the current repo state and recent codex/codex-web learnings.

    ## Current checkpoints
    - `pyproject.toml` provides project identity, install metadata, and broad dependency requirements.
    - No generated lockfiles or workflow YAMLs are committed; contributors install ad hoc.
    - The Tornado app, Behave scenarios, and Playwright support exist but are not enforced in CI.
    - Codex-focused detours taught us which steps unblock automation first (lint/test gating, repeatable local script, artifact handling later).

    ## Guiding principles
    1. Ship a trustworthy baseline pipeline before layering on heavier security/compliance.
    2. Keep developer friction low: editable sources remain in `pyproject.toml`; generated artifacts should never require hand edits.
    3. Prefer tooling that runs both locally and in GitHub Actions without Docker unless necessary.
    4. Treat SBOMs as a required outcome for releases, but allow the first CI merge to land without blocking on SBOM automation.
    5. Lean into `uv` for speed and reproducibility, while keeping plain `pip` fallbacks for contributors who do not have `uv` yet.

    ## Incremental work plan

    ### Phase A — Establish repeatable installs and scripts
    - Add `scripts/ci-local.sh` mirroring the eventual workflow steps (create venv, install editable project with `[test]` extras, run lint + pytest + behave smoke subset).
    - Detect `uv`; prefer `uv pip install -e .[test]`, otherwise fall back to `pip install -e .[test]`.
    - Document the command in `CONTRIBUTING.md` so new contributors can validate before opening PRs.
    - Verify the script against macOS dev environment (no containers yet).

    ### Phase B — Bootstrap GitHub Actions CI
    - Create `.github/workflows/test.yml` with Python `3.11` and `3.12` strategy, installing via `uv pip install -e .[test]` (with `pip` as contingency).
    - Run `ruff` (or `flake8` if ruff isn’t ready) and `pytest --maxfail=1 --disable-warnings`, then execute the full Behave suite with Playwright-backed scenarios since caching and the local script already keep runtimes acceptable.
    - Fail fast when dependency ranges pull incompatible versions; this exposes locking needs naturally.
    - Upload pytest cache, Playwright browser cache, or coverage artifacts if helpful for debugging (optional at this stage).

    ### Phase C — Introduce `uv` lockfiles for CI stability
    - Use `uv lock` (or `uv pip compile`) to produce `uv.lock` plus extracted `requirements.lock` and `requirements-dev.lock` for environments that still expect pip-style files.
    - Teach CI to prefer the lockfiles when they exist: `uv pip sync requirements-dev.lock`; fall back to editable install if locks are out of date.
    - Keep the editable install path (`pip install -e .`) for local dev; lockfiles become the safety net and CI default.
    - Update `scripts/ci-local.sh` to accept a `--locked` flag that uses the lockfiles via `uv pip sync`, enabling contributors to mimic CI behavior.

    ### Phase D — Add SBOM & dependency governance
    - Integrate CycloneDX generation into the workflow after tests succeed (produce `sbom.cdx.json` artifact sourced from the lockfile or venv).
    - Add Dependabot (initially targeting `pyproject.toml`, `uv.lock`, and exported lockfiles). Choose Renovate later if we want grouped update PRs or automated lock refreshes.
    - On release tags (`rel-*`), extend the workflow to attach SBOM and release notes artifacts.

### Phase E — Linting depth & quality automation
- **Static analysis hardening**
  - Promote `ruff` from optional to required in CI, enabling rule sets for import sorting, docstrings, and complexity checks.
  - Layer in type checking (`mypy` or `pyright`) with incremental enforcement, starting from the most critical modules.
- **Behavioral quality gates**
  - Ensure Behave tag usage matches agreed conventions (`@smoke`, `@javascript`), and add a check that fails on untagged UI scenarios.
  - Add snapshot-style checks for generated release notes to avoid regressions in formatting.
- **Automation polish**
  - Introduce pre-commit hooks (shared config) so contributors run lint/type checks locally before PRs.
  - Track lint baselines to prevent regressions (e.g., `ruff --exit-non-zero-on-fix` + summary artifact).
- **Documentation & onboarding**
  - Expand `CONTRIBUTING.md` with lint/type instructions and quick-fix commands.
  - Provide sample `uv run` aliases for common linting tasks to keep usage consistent between humans and CI.

    ## Acceptance signals per phase
    - **Phase A:** `scripts/ci-local.sh` succeeds on macOS; documented in `CONTRIBUTING.md`.
    - **Phase B:** GitHub Actions badge turns green on main; PRs blocked until pipeline passes.
    - **Phase C:** Lockfiles exist, CI uses them by default through `uv`; contributors can regenerate with a single command.
    - **Phase D:** SBOM artifact appears on CI runs that modify dependencies; Dependabot PRs open automatically.
- **Phase E:** Lint/type gates are required in CI, Behave tagging guardrails prevent accidental regressions, and pre-commit automation keeps churn low for contributors.

    ## Open questions to resolve during implementation
    - Which lint tool do we standardize on first (ruff vs pylint) given current code quality?
    - Do we commit both exported pip-style lockfiles and the native `uv.lock`, or rely solely on `uv` artifacts?
    - What is the minimum Behave tag set that gives confidence without slowing the pipeline?
- Which lint/type tools are authoritative (`ruff` vs `flake8`, `mypy` vs `pyright`) and how strict should initial baselines be?
- How do we phase in stricter linting without blocking current contributors (e.g., allow warnings, staged directories)?
- What conventions define acceptable Behave tags, and should we enforce them via custom lint rules?
- Do we vendor pre-commit hooks or rely on `uv tool run pre-commit` so CI and local flows stay in sync?

    ## Next action
    - Build `scripts/ci-local.sh` and validate it against the existing `pyproject.toml` dependencies. This is the enabling step for both developers and CI.

    ## Comments
    - 2025-10-09: Updated Phase B/E to reflect the current Python 3.11/3.12 matrix and confidence in running full Playwright-backed Behave coverage with caching.
    - 2025-10-09: Kicked off Phase C by generating uv-driven lockfiles, teaching CI to prefer them, and adding a `--locked` path to the local script for parity.
- 2025-10-09: Advanced Phase D by wiring cyclonedx SBOM generation (+ dependency graph via the CI virtualenv) and enabling Dependabot for Python locks and GitHub Actions.
- 2025-10-09: Spun off Phase E linting/quality issue to stage stricter static analysis and contributor tooling.
