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

    ### Phase E — Expand coverage (optional follow-ons)
    - Add deeper service integrations (for example Postgres-backed tests) when the app depends on external services.
    - Evaluate cross-browser Playwright runs or additional Python versions as long-term capacity improves.
    - Explore publishing Docker images or PyPI packages as part of releases once CI is stable.

    ## Acceptance signals per phase
    - **Phase A:** `scripts/ci-local.sh` succeeds on macOS; documented in `CONTRIBUTING.md`.
    - **Phase B:** GitHub Actions badge turns green on main; PRs blocked until pipeline passes.
    - **Phase C:** Lockfiles exist, CI uses them by default through `uv`; contributors can regenerate with a single command.
    - **Phase D:** SBOM artifact appears on CI runs that modify dependencies; Dependabot PRs open automatically.
    - **Phase E:** Broader test coverage runs without timeouts; optional release automation documented.

    ## Open questions to resolve during implementation
    - Which lint tool do we standardize on first (ruff vs pylint) given current code quality?
    - Do we commit both exported pip-style lockfiles and the native `uv.lock`, or rely solely on `uv` artifacts?
    - What is the minimum Behave tag set that gives confidence without slowing the pipeline?
    - Should SBOM generation be mandatory on every push, or only on `main` + releases?
    - How do we want Dependabot or Renovate PRs to interact with lockfile regeneration (manual vs CI-generated)?

    ## Next action
    - Build `scripts/ci-local.sh` and validate it against the existing `pyproject.toml` dependencies. This is the enabling step for both developers and CI.

    ## Comments
    - 2025-10-09: Updated Phase B/E to reflect the current Python 3.11/3.12 matrix and confidence in running full Playwright-backed Behave coverage with caching.
    - 2025-10-09: Kicked off Phase C by generating uv-driven lockfiles, teaching CI to prefer them, and adding a `--locked` path to the local script for parity.
    - 2025-10-09: Advanced Phase D by wiring cyclonedx SBOM generation (+ dependency graph via the CI virtualenv) and enabling Dependabot for Python locks and GitHub Actions.
