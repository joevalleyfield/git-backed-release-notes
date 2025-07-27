# Extract Follows/Precedes logic from handler to git utils

## Motivation

The `CommitHandler` was responsible for parsing both the `follows` and `precedes` tag information using `git describe`, `rev-list`, and `merge-base`. This logic was verbose, tightly coupled to subprocesses, and difficult to test in isolation.

## Change

The core logic for tag resolution was moved to `utils/git.py`, introducing two primary functions:

- `find_follows_tag(sha, repo_path, tag_pattern)`
- `find_precedes_tag(sha, repo_path, tag_pattern)`

These return structured objects and are now directly covered by unit tests.

In a follow-up, `find_precedes_tag` was further refactored to improve clarity and testability. Supporting helpers were introduced:

- `get_matching_tag_commits(repo_path, pattern)`: filters and resolves tags
- `get_topo_ordered_commits(repo_path)`: returns commits in topo-reverse order
- `is_ancestor(ancestor, descendant, repo_path)`: checks ancestry via `merge-base`

Each helper is independently tested, and the log message for a missing commit in topological order was promoted from debug to warning.

## Impact

- No change to observable behavior
- Full unit test coverage for all tag resolution logic
- Lays groundwork for reuse and cleaner testing in other modules (e.g., CLI or release views)
