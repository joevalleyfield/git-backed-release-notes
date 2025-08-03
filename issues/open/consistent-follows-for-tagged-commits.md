# 📎 Feature: Consistent `Follows:` for Tagged Commits

```yaml
tags: [graph-traversal, tag-logic]
status: open
```

## Problem

Tagged commits currently omit `Follows:` entirely. This breaks backward traversal and creates an asymmetry with `Precedes:`.

## Proposed Behavior

A commit's `Follows:` should always point to the **nearest preceding tag**, even if the commit is itself tagged.

### Example

Given:

```text
A --- B --- C --- D --- E
      ^           ^
    rel-1       rel-2
```

Expected:

- **D** (`rel-2`) → `Follows: rel-1`
- **C** → `Follows: rel-1`
- **B** (`rel-1`) → `Follows: (rel-0, if present)`
- **A** → no `Follows:`

## Rationale

- Enables symmetric and intuitive graph traversal.
- Clarifies commit-release lineage regardless of tagging.
- Simplifies test logic and release annotation features.

## Comments

2025.08.03.Su 1006
Human readable ref description disabled in implementation commit and re-enabled with follow-up.
