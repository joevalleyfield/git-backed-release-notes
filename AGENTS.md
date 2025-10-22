# Repository Guidelines

## Project Structure & Module Organization
- Core Tornado app lives in `src/git_release_notes/` with request handlers under `handlers/`, shared helpers in `utils/`, HTML templates in `templates/`, and vendored JS/CSS in `static/`.
- CLI and server entry points are `src/git_release_notes/__main__.py` and the `git-release-notes` console script; `app.py` just forwards to the package entry.
- Automated tests live in `tests/` (pytest unit suites plus shared fixtures in `tests/helpers/`) and `features/` (Behave scenarios with step code in `features/steps/`).
- Repository data fixtures (`commits.csv`, `git-view.metadata.csv`, issue notes) sit at the repo root so they can double as integration-test inputs.

## Build, Test, and Development Commands
- Bootstrap a dev install with `python -m pip install -e .[test]` (or `uv pip install -e .[test]`) to pull runtime plus lint/test extras.
- Run the full local gate via `./scripts/ci-local.sh`; it provisions a sandboxed venv, installs `[test]` deps, vendors Playwright browsers, and then runs Ruff, pytest, and Behave.
- Format and lint with `./scripts/run-black.sh` and `./scripts/run-ruff.sh`; both mirror CI checks.
- Type-check hot paths through `./scripts/run-mypy.sh`; expand coverage by updating `tool.mypy.files` when new modules graduate to strict typing.
- Launch the app using `python -m git_release_notes --repo ../path/to/git/clone` (or `git-release-notes ...`) and export `USE_LOCAL_ASSETS=1` if offline assets are required.

## Coding Style & Naming Conventions
- Python uses 4-space indents, 110-character lines, double quotes, and package-relative imports (`from git_release_notes.utils import ...`).
- Prefer explicit Tornado handler classes per route, keeping handler filenames snake_case and templates kabob-case (`commit-detail.html`).
- Run `pre-commit install` (via `uv tool run pre-commit install`) so Ruff, Black, and mypy guard every commit; fix warnings before re-running CI.

## Testing Guidelines
- Unit modules should follow `tests/unit/test_<subject>.py`; leverage `tests/helpers/` for reusable fixtures.
- Behave scenarios in `features/*.feature` should tag browser-dependent flows with `@javascript`; execute them after `pytest` via `behave` or `behave --tags ~@wip` while iterating.
- Keep reproducibility by resetting any temporary Git repositories created in tests and avoiding hard-coded commit SHAs outside fixtures.

## Commit & Pull Request Guidelines
- Adopt the existing Conventional Commit prefixes (`feat:`, `fix:`, `chore:`, `test:`, `docs:`); keep subjects in the imperative and wrap details in the body after a blank line.
- Reference related issue note files (for example, `issues/open/feature-x.md`) to tie execution steps back to planning artifacts.
- Pull requests should summarize behavior shifts, list the checks you ran (`./scripts/ci-local.sh`, `pytest`, `behave`), and attach screenshots when UI templates change.

## Contributor Workflow Tips
- Run `./scripts/setup_local_assets.sh` once per machine to download vendored frontend bundles; re-run `./scripts/refresh_vendor_assets.sh` after dependency bumps.
- Use `source scripts/aliases.sh` to load helper aliases (`ruff-run`, `black-run`, etc.) that align with our CI tooling.

## Jujutsu (jj) Practices We Use

### Draft → Reviewable → Publishable
- **Drafts**: everything in `mutable()`; rewrite/split/squash freely.
- **Reviewable**: still mutable, but given a topic bookmark (e.g., `tjm/foo`) so diffs are coherent.
- **Publishable**: protected bookmarks (`main`, `release/*`) are immutable—don’t rewrite without `--ignore-immutable`.

### Colocated behavior to remember
- Even “read-only” commands like `jj status`, `jj show`, or `jj log @` **refresh the working-copy commit**. In colocated repos this creates/updates a Git commit under `refs/jj/keep/*`. You may see new objects in Git just by running status—this is expected.

### Quick “tip-fix” pattern (don’t rewrite immutables)
If an accidental file slipped in (e.g., `update_foo.sh`):
```bash
# Start (or reuse) an empty change and state intent up front
jj describe -m "fix: remove stray update_foo.sh"

# Make the correction
rm update_foo.sh
jj status   # sanity check; jj has already recorded the deletion
```
For wide/structural bugs that must be inherited by branches from the old base, fork from the bad immutable and merge the fix forward; otherwise prefer the simple tip-fix.

### Issue notes: Postscript convention
Closed issues can record follow-ups without reopening:
```md
## Postscript
2025-10-22: removed stray `update_foo.sh` (change <change_id>)
```

**jj primer**: See [docs/jj-PRIMER.md](docs/jj-PRIMER.md) for a practical crash course.  
  This covers mental model, commands, intent-first workflow (`jj describe --stdin`),  
  template cheatsheet, and a Git → JJ mindset table. 

## “Mutable Courier” over Git (self-sync between machines)

We use Git as a **dumb transport** for mutable jj changes via a private refspace.

**Refspec (per repo, `.git/config`):**
```ini
[remote "origin"]
    fetch = +refs/heads/*:refs/remotes/origin/*
    fetch = +refs/jj/mutable/*:refs/jj/mutable/*
    push  = +refs/heads/*:refs/heads/*
    push  = +refs/jj/mutable/*:refs/jj/mutable/*
```

**Hide noisy colocated refs in Git tools (keep our courier visible):**
```ini
[transfer]
    hideRefs = refs/jj/
# (Our scripts reference refs/jj/mutable/* explicitly, so they remain usable.)
```

**Scripts (in `scripts/`)**
- `jj-push-mutable.sh <topic-or-change-id>` → writes current change’s `commit_id` to `refs/jj/mutable/<topic-or-change-id>` and pushes it.
- `jj-pull-mutable.sh <topic-or-change-id>` → fetches that ref and `jj checkout "git_ref(\"...\")"`.

**Common ops**
```bash
# list available courier refs on origin
git ls-remote origin "refs/jj/mutable/*"

# delete a mistaken remote ref
git push origin :refs/jj/mutable/pm

# remove local copy
git update-ref -d refs/jj/mutable/pm
```
This gives you “resume exactly where I left off” between laptop/desktop without publishing anything to normal branches.

