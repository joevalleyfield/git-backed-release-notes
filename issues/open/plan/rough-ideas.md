# Inception Log / Unrefined Ideas

## 📐 UX & Behavior

- auto-highlight-linked-issue-on-commit-page
- add sidebar nav to index page
- extract issue slugs from commit messages using `Resolves #<slug>`
- Auto-link commits to issues via slug mentions

## 🧪 Testing

- test-issue-linking-when-implemented
- test-precedes-annotated-vs-lightweight-tags

## 🛠️ Internal Code Quality

- Rename @with_xlsx → @requires_spreadsheet for clearer intent and future-proofing
  to clarify intended exports and avoid unintentional namespace leaks.
- Add `__all__` declarations to public-facing modules (e.g. handlers, utils, fixture support)
