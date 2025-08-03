# 📎 Feature: Consistent `Follows:` for Tagged Commits

```yaml
tags: [graph-traversal, tag-logic]
status: closed
```

## Problem

Tagged commits previously omitted `Follows:`, breaking backward traversal and creating an asymmetry with `Precedes:`.

## Resolution

`Follows:` now consistently points to the **nearest preceding tag**, even when the commit is itself tagged.

### Example

Given:

```text
A --- B --- C --- D --- E
      ^           ^
    rel-1       rel-2
```

Resolved behavior:

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
Human-readable ref description was temporarily disabled and re-enabled in a follow-up.
