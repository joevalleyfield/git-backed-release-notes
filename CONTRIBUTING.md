# Repository Guidelines

## Project Structure & Module Organization
- Application code lives in `src/git_release_notes/`, organized into `handlers/`, `utils/`, and Tornado templates under `templates/`.
- Entry point is `git_release_notes/__main__.py`; `app.py` is a compatibility shim.
- Tests reside in `tests/` (pytest) and `features/` (Behave BDD scenarios). Issue notes are tracked in `issues/open/` and `issues/closed/`.
- Static assets such as CSV fixtures or metadata live alongside the app (`git-view.metadata.csv`, `commits.csv`).

## Build, Test, and Development Commands
- Full check before a PR: `./scripts/ci-local.sh` provisions its own virtualenv, installs `[test]` extras with `uv` when available (falls back to `pip`), runs `ruff`, `pytest`, and a Behave smoke pass. Use `--skip-behave` while iterating.
- Launch the UI: `python -m git_release_notes --repo /path/to/repo [--excel-path commits.xlsx]` (console alias: `git-release-notes`).
- Install dev dependencies: `python -m pip install -e .[test]` (or `uv pip install -e .[test]`) to get runtime + test extras.
- Package the project: `python -m build` (requires `pip install build`).
- Run unit tests: `pytest` from the repo root.
- Execute end-to-end tests: `behave` (spawns Tornado servers on localhost ports 8888+; ensure ports are free).
- Frontend libraries are vendored under `src/git_release_notes/static/vendor/`. Use `./scripts/setup_local_assets.sh` to download them (or `./scripts/refresh_vendor_assets.sh` to force an update) before running in offline environments. Set `USE_LOCAL_ASSETS=1` when you need to bypass the CDN entirely.

## Coding Style & Naming Conventions
- Python code follows PEP 8 with 4-space indentation; keep modules ASCII-only unless a file already contains Unicode.
- Prefer package-relative imports (e.g., `from git_release_notes.utils import ...`).
- Handlers expose Tornado `RequestHandler` subclasses; new handlers belong in `src/git_release_notes/handlers/`.
- Template files use Tornado's template language and lowercase kabob-case names (e.g., `commit.html`).

## Testing Guidelines
- Unit tests live in `tests/unit/` with filenames `test_*.py`; add fixtures to `tests/helpers/` when needed.
- Behave steps are under `features/steps/`; tag web-driven scenarios with `@javascript` only when Playwright interaction is required.
- Always run `pytest` before `behave`; Behave depends on a clean local Git repo and open localhost ports.

## Commit & Pull Request Guidelines
- Follow existing prefixes: `feat:`, `fix:`, `docs:`, `build:`, `test:`, `issue: close ...`, etc. Use imperative mood (e.g., `feat: migrate entry point into src layout`).
- Reference related issue files in the description (e.g., "See `issues/open/suggest-issues-on-index.md`").
- PRs should summarize behavior changes, note testing performed (`pytest`, `behave`), and include screenshots for UI shifts when practical.
