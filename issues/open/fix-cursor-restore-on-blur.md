# Bug: Cursor incorrectly restored after blur save

    ```yaml
    tags: [bug, ui, inline-edit]
    status: open
    planned-release: rel-0.6
    ```

## Behavior

- On pressing **Enter**, the cursor and caret should be restored after a successful save.  
- On **blur** (clicking away), the cursor should not return to the edited field.  

## Current Problem

After the initial implementation, blur saves were restoring focus to the edited field, which was annoying when intentionally clicking elsewhere. A minimal patch fixed this by removing forced focus on blur, but we need to ensure the behavior stays correct and is covered by tests.

## TODO

- [ ] Add a feature test scenario:
  - Given a known commit  
  - When the user edits a field and clicks away  
  - Then the cursor should **not** be restored to that field after save  
- [ ] Ensure Enter-triggered saves continue to restore caret position as intended

