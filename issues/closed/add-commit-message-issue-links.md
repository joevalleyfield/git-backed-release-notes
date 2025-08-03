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
references to issue slugs in commit messages. The system recognizes:

- `#slug` style mentions
- `slug.md` file-style mentions
- plain kabob-case slugs (e.g., `my-feature`, `foo-bar-baz`)

When a commit references multiple issues, the system:

- Links to **all matched slugs** in the commit detail view
- Chooses **one primary issue** for attribution when possible

### Directive Matching

The parser is designed to be **lenient** and real-world friendly. Recognized
directive verbs include:

- `fix`, `fixes`, `fixed`
- `close`, `closes`, `closed`
- `resolve`, `resolves`, `resolved`
- `implement`, `implements`, `implemented`

These verbs are matched case-insensitively, with or without a colon, and can be
followed by:

- `#slug`
- `slug.md`
- `some-slug` (kabob-case only)

For example, the following lines all identify `my-feature` as a reference:

- `Fixes #my-feature`
- `Resolves my-feature.md`
- `Implements: my-feature`

Directive-based matches are used to determine *primary attribution*.

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
