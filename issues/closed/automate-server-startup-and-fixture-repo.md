# Automate server startup and fixture repo

## Goal

Enable end-to-end tests to start the server automatically with a temporary fixture repo, eliminating the need for manual startup and shared local repo state.

## Tasks

- [X] Create a minimal Git repo fixture (`.git` + 1–2 commits and tags)
- [X] Create temporary `.xlsx` input file for test
- [X] Launch the Tornado app server in a subprocess from `before_all`
- [X] Pass fixture repo path as CLI arg to app
- [X] Wait for server readiness before tests proceed
- [X] Shut down server after all tests complete
- [X] Clean up temp repo directory

## Motivation

This lays the foundation for reproducible, self-contained end-to-end tests.
