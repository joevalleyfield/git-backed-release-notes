# Add Styling

Track planned styling improvements across the app, with a focus on clean
defaults, semantic HTML, and graceful fallback when JavaScript is disabled.

## Goals

- Introduce a clean, readable layout for all views
- Ensure the site remains fully usable without JavaScript
- Preserve embedding of structured data for progressive enhancement

## Completed Work

- [x] Add Bootstrap 5 for baseline layout and responsive styling
- [x] Integrate Diff2Html for improved diff rendering
- [x] Replace raw `<pre>` diff block with dynamic Diff2Html output
- [x] Pre-render HTML diffs for no-JS fallback on commit pages (via `output_header`)
- [x] Improve form and table styling using Bootstrap classes
- [x] Modernize index and commit detail pages with better layout and spacing

## Planned Work

- [x] Remove unused `Markup` wrapping and custom `tojson` namespace helper
- ~~[ ] Refine commit detail page layout (spacing, hierarchy, metadata)~~
- [x] Improve scan-ability of index/list pages
- ~~[ ] Apply consistent styling to headers, metadata, and diffs~~
- [x] Use semantic HTML tags (`<main>`, `<section>`, etc.)
- ~~[ ] Customize Diff2Html theme (optional)~~

## Notes

This issue guides ongoing styling work. Functional priorities include readable
diffs without JS, visually organized metadata, and consistent layout and
typography across all views. With Bootstrap and Diff2Html integrated, the next
step is refining details and ensuring semantic markup and visual clarity
throughout.

## Comments

2025.07.19.Sa 0859

- Fix test regression caused by text change in back link.

---
2025.07.19.Sa 1149

- Removed unused `tojson` helper and `Markup` import after confirming Tornado's built-in `json_encode` is sufficient for template usage.

---
2025.07.19.Sa 1236

- Upgraded `commit.html` and `index.html` to use semantic HTML elements (`<main>`, `<header>`, `<section>`, `<footer>`, etc.)
- Preserved all Bootstrap styling while improving document structure and accessibility.

---
2025.07.19.Sa 1604

- Removed unnecessary `id` column from index table
- Reordered columns to improve scan-ability: `sha`, `message`, `issue`, `release`, `date`
- Layout now prioritizes human-readable context over backend artifacts

---
