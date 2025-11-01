# Issue-Centric Browsing Index

```yaml
tags: [issues, index, navigation]
status: closed
```

Created an issue-centric browsing surface that mirrored the existing commit
index so contributors could scan every issue—open or closed—in historical
context, including sorting and grouping by release to reflect issue-release
coupling.

## Behavior Tree

- **Root Goal**: Delivered a chronological issue index

  - [A] **Date-Oriented Timeline**
    Listed issues in descending order by creation/last-updated date to support
    fast recency checks.

  - [B] **History-Oriented Timeline**
    Offered an alternate view that ordered issues by when their linked commits
    landed, aligning issue review with repository history.

  - [C] **Status Cohesion**
    Included both open and closed issues in a single index with clear status
    badges, so context switching between queues was minimized.

  - [D] **Release Cohorts**
    Enabled filtering and grouping by release so issue-review flows aligned with
    planned or shipped milestones.

  - [E] **Commit Crosslinks**
    Surfaced backlinks to the commit index (and commit-detail pages) to make it
    easy to jump between issue discussions and the code changes that resolved
    them.

## BDD Implementation Tasks (First Draft)

1. [x] Captured acceptance criteria in a new `features/issue_index.feature` describing date-view, history-view, release grouping, and crosslinks.
2. [x] Sketched supporting fixtures in `tests/helpers/` (issue metadata, commit mappings) to keep Behave scenarios deterministic.
3. [x] Added pending step definitions in `features/steps/issue_index_steps.py`, wiring placeholders to clarify data setup, navigation, and assertions.
4. [x] Extended the Tornado route table to expose an `/issues` handler returning a template-ready payload that included status, release, and landing metadata.
5. [x] Implemented repository/query helpers in `git_release_notes/utils/` to collect issues, resolve release associations, and join commit timestamps.
6. [x] Built the index template under `templates/` with toggles for chronological vs landing order and inline release grouping UI.
7. [x] Fleshed out the Behave steps to drive the page, assert ordering/grouping, and verify crosslinks against fixture data.
8. [x] Backfilled unit coverage for the new query helpers (e.g., `tests/unit/test_issue_queries.py`) and any release-filter combinators.
9. [x] Integrated the issue index link into existing navigation (CLI/server) and ensured the commit index referenced the new view where appropriate.
10. [x] Refreshed documentation or onboarding notes (README, help text) to surface the issue browsing workflow once behaviors passed.
