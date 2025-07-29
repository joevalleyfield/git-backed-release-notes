# 🧩 Add Commit Message Issue Links

Enable automatic linking between commits and issues when an issue slug (e.g. `#my-feature`) appears in the commit message body.

```yaml
tags: [linking, feature, commit-metadata]
status: open
planned-release: rel-0.4
```

## Motivation

Currently, commits are linked to issues only when explicitly annotated via the `issue` field in `git-view.metadata.csv` or through the commit edit UI. However, it’s common to mention issues inline in commit messages using `#slug` syntax.

This feature implements automatic detection and linking behavior when a commit message references an existing issue slug.

## Acceptance Criteria

- [X] Commits with message text that includes `#issue-slug` should:
  - [X] Link to `/issue/issue-slug` in the commit detail view
  - [X] Appear in the referring commit list on the issue detail page
- [X] References can occur mid-line (e.g., `Fixes #my-feature`) or standalone
- [X] Parsing should support multiple references in a single message
  - [X] One of these should be treated as the *primary* issue for attribution

## Design Notes

This feature adds lightweight linking between commits and issues by parsing
`#slug` references in commit messages. When a commit references multiple issues,
the system:

- Links to **all referenced slugs** for context and navigation
- Chooses **one primary issue** for attribution when possible

### Directive Matching

The parser should be **lenient** and focus on capturing intent over format. Recognized directives include verbs like:

- `fix`, `fixes`, `fixed`
- `close`, `closes`, `closed`
- `resolve`, `resolves`, `resolved`
- `implement`, `implements`, `implemented`

These may appear with or without a colon (e.g., `Fixes #abc`, `Resolves: #def`),
and are matched case-insensitively. This ensures compatibility with real-world
commit styles and behaviors seen in GitHub, GitLab, and Jira.

Additional mentions like `#related-thing` will still be recognized and linked,
but only directive matches influence primary attribution.

### Primary Attribution Heuristics

When a commit references or implies multiple issues, apply the following logic
to determine its *primary* issue:

1. **Directive-based mention (preferred):**  
   If the message contains a verb like `Fixes`, `Resolves`, or `Implements` followed by a `#slug`, the first such reference determines the primary.

2. **Touched issue file fallback:**  
   If the commit touches exactly one issue file (e.g., `my-feature.md`), and no directive-based reference exists, that slug is treated as the primary.

3. **No primary:**  
   If neither condition is met, the commit links to referenced slugs for navigation only, with no canonical attribution.

This layered approach balances automation with the flexibility needed for early
commits, exploratory work, and human inconsistency.
