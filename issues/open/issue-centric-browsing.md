# 📎 Task: Add Issue-Centric Browsing Index

```yaml
tags: [issues, index, navigation]
status: open
```

Create an issue-centric browsing surface that mirrors the existing commit index,
so contributors can scan every issue--open or closed--in historical context,
including sorting and grouping by release to reflect issue-release coupling.

## Behavior Tree

- **Root Goal**: Provide a chronological issue index

  - [A] **Date-Oriented Timeline**
    List issues in descending order by creation/last-updated date to support
    fast recency checks.

  - [B] **History-Oriented Timeline**
    Offer an alternate view that orders issues by when their linked commits
    landed, aligning issue review with repository history.

  - [C] **Status Cohesion**
    Include both open and closed issues in a single index with clear status
    badges, so context switching between queues is minimized.

  - [D] **Release Cohorts**
    Enable filtering and grouping by release so issue-review flows align with
    planned or shipped milestones.

  - [E] **Commit Crosslinks**
    Surface backlinks to the commit index (and commit-detail pages) to make it
    easy to jump between issue discussions and the code changes that resolved
    them.

## BDD Implementation Tasks (First Draft)

1. [x] Capture acceptance criteria in a new `features/issue_index.feature` describing date-view, history-view, release grouping, and crosslinks.
2. [x] Sketch supporting fixtures in `tests/helpers/` (issue metadata, commit mappings) to keep Behave scenarios deterministic.
3. [x] Add pending step definitions in `features/steps/issue_index_steps.py`, wiring placeholders to clarify data setup, navigation, and assertions.
4. [x] Extend the Tornado route table to expose an `/issues` handler returning a template-ready payload that includes status, release, and landing metadata.
5. [x] Implement repository/query helpers in `git_release_notes/utils/` to collect issues, resolve release associations, and join commit timestamps.
6. [x] Build the index template under `templates/` with toggles for chronological vs landing order and inline release grouping UI.
7. [x] Flesh out the Behave steps to drive the page, assert ordering/grouping, and verify crosslinks against fixture data.
8. [x] Backfill unit coverage for the new query helpers (e.g., `tests/unit/test_issue_queries.py`) and any release-filter combinators.
9. [x] Integrate the issue index link into existing navigation (CLI/server) and ensure the commit index references the new view where appropriate.
10. [ ] Refresh documentation or onboarding notes (README, help text) to surface the issue browsing workflow once behaviors pass.
