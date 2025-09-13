# Fix: Cursor incorrectly restored after blur save

```yaml
tags: [bug, ui, inline-edit]
status: closed
```

## Behavior

- On pressing **Enter**, the cursor and caret should be restored after a successful save.  
- On **blur** (clicking or tabbing away), the cursor should not return to the edited field.  

## Resolution

- Refactored save logic into `async saveInputChange(input, {restoreCursorOnSave})`.  
- Blur-triggered saves no longer snap the cursor back.  
- Enter-triggered saves continue to restore focus and caret position.  
- Playwright step definitions consolidated:  
  - *click away* deterministically moves to sibling input.  
  - *tab away* observes `document.activeElement` instead of predicting.  
- Feature tests extended to cover both blur and tab-away flows, with explicit focus assertions and page reload validation.

## Outcome

The unwanted cursor snapback on blur is fixed, behavior is predictable across both interaction modes, and regression coverage is in place via feature tests.
