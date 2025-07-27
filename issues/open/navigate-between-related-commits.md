# Feature: Navigate Between Related Commits

## Motivation

The commit detail view previously lacked any contextual navigation. To inspect adjacent or related commits, users had to back out to the index page. This made reviewing commit relationships tedious and nonlinear.

## Original Goal

- Add navigation links for "Previous" and "Next" commits in time order

## Evolution

While working on this, we realized that linear ordering (like from `df`) was ambiguous or unavailable in no-spreadsheet mode. Instead, we pivoted to use the Git commit graph:

- "Parents" = first-degree ancestors
- "Children" = commits for which the current commit is a parent

This provides richer and more accurate navigation for:
- Merge commits
- Branches and rebases
- Annotated Git histories

## Implementation

- Added `get_commit_parents_and_children()` helper using `git show` and `rev-list --children`, with caching
- Updated `CommitHandler` to compute and pass `parents` and `children`
- Rendered these links in the commit template
- Added behave feature test for presence of navigation links

## Status

✅ Feature implemented  
✅ Tests written  
🚫 No additional follow-up planned
