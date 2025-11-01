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
