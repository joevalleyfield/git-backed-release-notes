
# Unexpected Missing `Precedes` Tag on Some Commits

In some cases, I expect a `Precedes:` tag to appear for a commit, but it does not.  
These commits are not themselves tagged, but I believe they have a descendant that is.

## Hypothesis

Possibilities include:

- The descendant tag exists, but is not reachable by topo-order from the commit
- The tag pattern used (`rel-*`) might not match the relevant tag
- The descendant commit is on a different branch not merged into `main` or `HEAD`
- Bug in the `find_precedes_tag()` logic, e.g., rev-list or index lookup

## Next Steps

- [X] Confirm that the descendant tag SHA is truly a descendant of the commit using:

```bash
  git merge-base --is-ancestor <commit> <tag>
```

- [X] Verify that the tag is included in `git tag --list "<pattern>"`
- [ ] Add debugging output or logs inside `find_precedes_tag()`
- [ ] Consider caching `rev-list` and tag lookup for performance

## Affected Example(s)

- Commit: `a34e7e8263a3b4a09a0b3b1661bf8a549c636f5e`
- Expected `Precedes:`: `rel-4-23-0`

## Related Issues

- [`add-debug-output-to-precedes-search`](add-debug-output-to-precedes-search.md)

## Comments

2025.07.10.Th
✅ Confirmed that git merge-base --is-ancestor returns 0, meaning the tag is a descendant.
✅ Confirmed that git rel-4-23-0 is returned by git tag --list "rel-*".
