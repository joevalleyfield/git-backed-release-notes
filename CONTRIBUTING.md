# Repository Guidelines

## Project Structure & Module Organization
- Application code lives in `src/git_release_notes/`, organized into `handlers/`, `utils/`, and Tornado templates under `templates/`.
- Entry point is `git_release_notes/__main__.py`; `app.py` is a compatibility shim.
- Tests reside in `tests/` (pytest) and `features/` (Behave BDD scenarios). Issue notes are tracked in `issues/open/` and `issues/closed/`.
- Static assets such as CSV fixtures or metadata live alongside the app (`git-view.metadata.csv`, `commits.csv`).

## Build, Test, and Development Commands
- Full check before a PR: `./scripts/ci-local.sh` provisions its own virtualenv, installs `[test]` extras with `uv` when available (falls back to `pip`), installs Playwright browsers, then runs `ruff`, `pytest`, and the full Behave suite (including `@javascript`). Use `--locked` to sync against `requirements-dev.lock`, or `--skip-behave` / `--skip-playwright-install` while iterating.
- Lint the repo: run `./scripts/run-ruff.sh` (or `uv tool run ruff check .`); CI enforces the same rules.
- Format code: run `./scripts/run-black.sh` to apply Black’s formatting (CI verifies with `--check`).
- Type-check hot paths: run `./scripts/run-mypy.sh` (currently targets `src/git_release_notes/utils`).
- Install pre-commit hooks: `uv tool run pre-commit install` so lint/format/type checks run before each commit; `./scripts/run-precommit.sh run --all-files` mirrors CI.
- Optional aliases: `source scripts/aliases.sh` to expose `ruff-run`, `black-run`, `mypy-run`, and `pre-commit-run` shortcuts.
- Generate an SBOM matching CI: `uv tool run --from cyclonedx-bom cyclonedx-py environment .venv-ci-local --pyproject pyproject.toml --of JSON --output-file sbom.cdx.json`.
- Launch the UI: `python -m git_release_notes --repo /path/to/repo [--excel-path commits.xlsx]` (console alias: `git-release-notes`).
- Install dev dependencies: `python -m pip install -e .[test]` (or `uv pip install -e .[test]`) to get runtime + test extras.
- Package the project: `python -m build` (requires `pip install build`).
- Run unit tests: `pytest` from the repo root.
- Execute end-to-end tests: `behave` (spawns Tornado servers on localhost ports 8888+; ensure ports are free). We standardize on Behave 1.3+, which preserves trailing punctuation in step text.
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
- Start the subject line with the established prefixes: `feat:`, `fix:`, `docs:`, `build:`, `test:`, `issue:`, etc., and keep the verb in imperative mood (e.g., `feat: migrate entry point into src layout`). When using tools like `jj describe`, leave a blank line between the tagged subject and the body for readability.
- Use `issue:` commits to open, update, or close issue notes when a conventional tag such as `docs:` would be misleading; for example, `issue: wrap up bootstrap-ci plan`.
- Reference related issue files in the description (e.g., "See `issues/open/suggest-issues-on-index.md`").
- PRs should summarize behavior changes, note testing performed (`pytest`, `behave`), and include screenshots for UI shifts when practical.

## JJ-Specific Collaboration Playbook

### Our change states
- **Drafts**: `mutable()`; rewrite at will.
- **Reviewable**: drafts you’ve named with a topic bookmark (`tjm/*`) for coherent diffs.
- **Publishable**: commits under `main` / `release/*` are **immutable** by policy.

### Colocated reality: “observing” snapshots the working copy
- Commands like `jj status`, `jj show`, or `jj log @` refresh the working-copy commit. In colocated repos that means new/updated Git objects under `refs/jj/keep/*`. Seeing churn there is normal.

### Tip-fix vs patch-in-place
- **Tip-fix (default):** add a new change now (or edit your current empty change), describe first, then make the correction. Don’t rewrite immutables.
  ```bash
  jj describe -m "fix: remove stray update_foo.sh"
  rm update_foo.sh
  jj status
  ```
- **Patch-in-place:** only when descendants *must* inherit the fix; fork from the old immutable and merge forward.

### Issue notes: `## Postscript`
Add follow-ups to closed issues without reopening them:
```md
## Postscript
YYYY-MM-DD: short note (change <change_id>)
```

## “Mutable Courier” (self-sync drafts via Git refs)

We use Git as a transport for JJ’s mutable state under `refs/jj/mutable/*`.

**Per-repo `.git/config`:**
```ini
[remote "origin"]
    fetch = +refs/heads/*:refs/remotes/origin/*
    fetch = +refs/jj/mutable/*:refs/jj/mutable/*
    push  = +refs/heads/*:refs/heads/*
    push  = +refs/jj/mutable/*:refs/jj/mutable/*
[transfer]
    hideRefs = refs/jj/
```
> We explicitly reference `refs/jj/mutable/*` in our scripts, so `hideRefs` won’t block usage; it just keeps other `refs/jj/*` noise out of Git tooling.

**Helper scripts (in `scripts/`)**
- `jj-push-mutable.sh <topic-or-change-id>` → points `refs/jj/mutable/<…>` at the current change’s **commit** and pushes it.
- `jj-pull-mutable.sh <topic-or-change-id>` → fetches and `jj checkout`’s the courier ref.

**Handy commands**
```bash
# enumerate courier refs on the remote
git ls-remote origin "refs/jj/mutable/*"

# delete an accidental remote ref
git push origin :refs/jj/mutable/NAME
git update-ref -d refs/jj/mutable/NAME  # local cleanup
```

**Listing namespaces (discovery without guessing)**
```bash
git ls-remote origin | cut -f2 | cut -d/ -f1-2 | sort -u         # top-level
git ls-remote origin | grep '^refs/jj/' | cut -d/ -f1-3 | sort -u # under refs/jj/
```

## Shell aliases & tracing

- We auto-alias `scripts/jj-*.sh` via:
  ```bash
  # in scripts/aliases.sh
  if [ -x ./scripts/jj-gen-aliases.sh ]; then
    source <(./scripts/jj-gen-aliases.sh)
  fi
  ```
  The generator skips itself, so you won’t get a `jj-gen-aliases` alias.

- Trace a helper cleanly (no prompt noise):
  ```bash
  zsh -x ./scripts/jj-push-mutable.sh mytopic
  # or bash -x ...
  ```
