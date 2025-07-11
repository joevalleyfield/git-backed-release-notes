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
