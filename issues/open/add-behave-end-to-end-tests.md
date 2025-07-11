# Add behave-Based End-to-End Tests

Introduce an end-to-end test suite using `behave` and `requests` to verify expected user-visible behavior across the Git Viewer web interface.

This provides a structured way to validate real behavior using Given/When/Then specifications that align with intent-driven development and issue tracking.

## Goals

- Define and document expected behavior at the feature level
- Automatically test core flows such as:
  - Commit index rendering
  - Commit detail view
  - Follows/Precedes tag resolution
  - Issue column visibility
  - Issue page rendering
- Establish the `features/` directory with Markdown-like test specifications

## Stack

- [`behave`](https://github.com/behave/behave): feature-file-based BDD
- [`requests`](https://docs.python-requests.org/): HTTP client used in steps
- Assumes the Tornado server is running on `localhost:8888`

## Initial Test Plan

Create test features such as:

- `features/index.feature`  
  Verifies that the commit index page loads and contains expected headings/content

- `features/commit_detail.feature`  
  Validates the commit detail page renders and includes correct links or tag references

- `features/issue_links.feature`  
  Verifies that issue slugs (if present) render as links

## Completed

- [X] Add `features/` directory and basic `index.feature`
- [X] Define initial `steps/index_steps.py`
- [X] Include a `test_server_is_running` scenario for baseline sanity

## Next Steps

- Later: test flows with temporary repo or dataset injected via fixture

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

## Related Features

- `automate-server-startup-and-fixture-repo.md`

## Comments

### 2025.07.11.Fr

Initial feature test (`index.feature`) and steps file added. Root page loads and contains expected content (assuming user/tester manually started the app server).
