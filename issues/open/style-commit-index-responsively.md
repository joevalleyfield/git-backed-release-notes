# Responsive, dense commit index (table → cards)

---

- tags: [ui, responsive, table, cards, density] 
- status: open 
- planned-release: rel-0.7

---

## Goal

Make the commit index usable across widths: dense, fixed-width columns on desktop; compact card-style rows on narrow screens. Preserve inline editing for `issue` and `release` without crowding link icons.

## Changes

- Apply card layout below **60rem**: hide `<thead>`, stack cells, reduce padding.
- Add column classes (`.col-sha`, `.col-message`, `.col-issue`, `.col-release`, `.col-date`) and fixed widths only at ≥60rem.
- Let **message** consume remaining width; truncate with ellipsis; click to expand/collapse.
- Add placeholders `(no issue)` / `(no release)` when empty.
- Use `width: calc(100% - 2em)` for inputs so link icon fits.
- Remove `.table-responsive` wrapper causing stray horizontal scroll.

## Exit Criteria

- Below 60rem, rows render as compact cards; no horizontal scroll.
- At ≥60rem, SHA/issue/release/date widths are respected; message takes the rest.
- Long messages truncate with ellipsis and expand on click.
- `issue`/`release` inputs don’t overlap link icons.
- No redundant labels on cards; placeholders appear only when fields are empty.

## Notes

- Breakpoint uses **rem** to scale with base font size.
- Future: replace inputs with “flat” read view that swaps to input on focus/edit.
