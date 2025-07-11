# Add End-to-End Test Framework

Introduce automated end-to-end tests to validate:

- Index rendering
- Commit detail page
- Tag resolution (follows/precedes)
- Issue metadata display
- Eventual issue editing and merges

## Goals

- Prevent regressions in UI logic and Git wiring
- Validate real paths through the system
- Support CLI and web flows

## Proposed Stack

- `behave` + `requests` for server testing
- `pytest` + `subprocess` for Git/CLI testing
- (Optional later) Playwright or Selenium for UI interaction

## First Steps

- Start web app on localhost in fixture
- Load minimal sample data
- Validate index and commit routes

## Related Issues

- `add-behave-end-to-end-tests.md`

## Comments

### 2025.07.11.Fr

Initial framework is now in place:

- Behave + requests drive full-stack server tests
- Fixtures start the app server and inject test repos
- Commit detail and tag logic now covered via Gherkin

This issue’s broader intent is fulfilled via add-behave-end-to-end-tests.md, now closed.
Remaining enhancements (CLI tests, issue interactions, UI automation) will be tracked separately if pursued.

Closing to reflect current scope.
