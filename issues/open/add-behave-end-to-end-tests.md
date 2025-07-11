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

## Next Steps

- Add `features/` directory and basic `index.feature`
- Define initial `steps/index_steps.py`
- Optionally include a `test_server_is_running` scenario for baseline sanity
- Later: test flows with temporary repo or dataset injected via fixture
