# Feature: Build Release Notes UX

## Motivation

We already persist `release` metadata alongside commits and surface tag suggestions, but `/release/<slug>` links still 404. Without dedicated views, teams can’t pull commits, issue notes, and release context together inside the app.

## Goals

- Add routes/handlers/templates for a release index and release detail page.
- Present release bundles with commits, linked issues, and rendered Markdown notes.
- Reuse the existing metadata store so edits stay consistent across views.
- Ensure commit and issue pages link cleanly into the new release screens.

## Acceptance Criteria

- `/release/<slug>` renders a populated detail view instead of 404.
- Release index is reachable from primary navigation and lists known releases.
- Commit/issue pages show working links to their releases.
- Tests cover new handlers (unit) plus a Behave happy path for one release.
- Docs mention the release-notes workflow and new navigation.

## Stretch Ideas

- Surface tag metadata (matching Git tags, inferred release dates).
- Offer export/download of release bundles (Markdown or HTML).
- Add filters (status, tag pattern, timeframe) on the release index.
