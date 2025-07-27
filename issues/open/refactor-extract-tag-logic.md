# Extract Follows/Precedes logic from handler to git utils

## Motivation

The `CommitHandler` is currently responsible for parsing both the `follows` and `precedes` tag information using `git describe`, `rev-list`, and `merge-base`. This logic is verbose, tightly coupled to subprocesses, and difficult to test in isolation.

## Change

This refactor moves the logic into `utils/git.py`, creating two new public functions:

- `find_follows_tag(sha, repo_path, tag_pattern) -> SimpleNamespace | None`
- `find_precedes_tag(sha, repo_path, tag_pattern) -> SimpleNamespace | None`

These return objects with the same structure as before, but can now be directly tested.

Test coverage was added for both functions in a new test module. The `CommitHandler` now delegates to these utilities and only passes the required arguments.

## Impact

- No change to observable behavior.
- Enables unit testing for tag resolution without requiring Tornado app scaffolding.
- Prepares the way for reuse elsewhere in the app (e.g., release views or CLI).
