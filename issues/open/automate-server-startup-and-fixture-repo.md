# Automate server startup and fixture repo

## Goal

Enable end-to-end tests to start the server automatically with a temporary fixture repo, eliminating the need for manual startup and shared local repo state.

## Tasks

- [ ] Create a minimal Git repo fixture (`.git` + 1–2 commits and tags)
- [ ] Launch the Tornado app server in a subprocess from `before_all`
- [ ] Pass fixture repo path as CLI arg to app
- [ ] Wait for server readiness before tests proceed
- [ ] Shut down server after all tests complete
- [ ] Clean up temp repo directory

## Motivation

This lays the foundation for reproducible, self-contained end-to-end tests.
