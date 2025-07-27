# Extract Follows/Precedes logic from handler to git utils

## Motivation

The `CommitHandler` was responsible for parsing both the `follows` and `precedes` tag information using `git describe`, `rev-list`, and `merge-base`. This logic was verbose, tightly coupled to subprocesses, and difficult to test in isolation.

## Change

The core logic for tag resolution was moved to `utils/git.py`, introducing two primary functions:

- `find_follows_tag(sha, repo_path, tag_pattern)`
- `find_precedes_tag(sha, repo_path, tag_pattern)`

These return structured objects and are now directly covered by unit tests.

In follow-up commits, the `find_precedes_tag` function was decomposed into reusable helpers:

- `get_matching_tag_commits(repo_path, pattern)`
- `get_topo_ordered_commits(repo_path)`
- `is_ancestor(ancestor, descendant, repo_path)`
- `get_tag_commit_sha(tag, repo_path)`
- `parse_describe_output(raw)`

Negative-path cases were added for test coverage, and all public helpers are documented with consistent return signatures.

## Impact

- `CommitHandler` is now cleaner and focused only on orchestration
- All subprocess-heavy Git logic is isolated and tested
- Functions are reusable across the app and suitable for CLI or release tooling
- No changes to observable behavior

## Status

This refactor is complete and the issue is now closed.