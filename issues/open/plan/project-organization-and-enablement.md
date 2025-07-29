# Project Organization and Enablement

This document captures two things:

- ✅ **Current actionable priorities** to guide near-term development
- 🧠 **Structural features** that help both humans and assistants collaborate effectively in this project

---

## ✅ Phase 1: Current Open Issues and Prioritization

| Priority | Task / Feature | Status | Why Now |
|---------:|----------------|--------|---------|
| 🔹 High | **Implement test: issue linking** | In `rough-ideas.md` | UI already works — test confirms cross-link behavior |
| 🔹 High | **Extract `Resolves #slug` from commit messages** | In `rough-ideas.md` | Automates linking, low-lift and high-value |
| 🔸 Med | **Inline editing on index page** | `inline-edit-release-and-issue.md` | UX improvement; needs JS wiring and backend save logic |
| 🔸 Med | **Manage issue file state UX** | `manage-issue-ui-state-and-working-tree-structure.md` | Infrastructure exists; feedback on missing or dirty files is weak |
| 🔸 Med | **Rename `@with_xlsx` → `@requires_spreadsheet`** | `rough-ideas.md` | Clarifies test behavior, improves filtering |
| 🔸 Med | **Add `__all__` declarations to modules** | `rough-ideas.md` | Clarifies public API, supports monolith bundling |
| 🔹 Low | **Sidebar nav or layout polish** | `rough-ideas.md` | Nice-to-have, not essential pre-release |
| 🔹 Low | **Test: annotated vs lightweight `Precedes:` tags** | `rough-ideas.md` | Edge case test, easy to postpone |

---

## 🧠 Phase 2: Features That Enable Human-AI Project Synergy

These structural enhancements make it easier for users to stay organized, and for an assistant to provide relevant, actionable help.

### 📎 1. Frontmatter Metadata in Issues

Support lightweight metadata headers in `.md` issue files:

    # Feature: Auto-link Commit Messages to Issues

    ```yaml
    tags: [linking, automation]
    status: open
    planned-release: rel-0.4
    ```

Benefits:

- Enables filtering, prioritization, and summarization
- Makes it easier for tools to group or query issues

### 🔗 2. Explicit Task Dependencies

Allow issues to declare dependencies in-body:

depends_on: [#inline-edit-release-and-issue]
blocks: [#auto-highlight-linked-issue]

Benefits:

- Enables task graph modeling
- Helps determine unblock conditions for features

### ✅ 3. Richer Commit References

Expand commit footers beyond just Closes: to include:

Refs: #foo
Blocked-by: #bar

Benefits:

- Improves traceability from commits to feature evolution
- Enables changelog and impact inference

### 📂 4. Discoverable Project Layout

Document or expose the structure:

    project.yaml
    |
    |- issues/
    |- features/
    |- templates/
    |- handlers/

Benefits:

- Lets humans or tools orient themselves quickly
- Makes assistant tooling more aware of structure-to-feature mapping

### 🔍 5. Support Natural Language Queries

With the above enhancements in place, queries like the following become answerable:

“What’s still left to do for inline editing?”
“What’s blocking rel-0.4?”
“What commit implemented parent-child navigation?”
