# Style the Issue Detail Page

## 🎯 Bob Bob Bob

- Apply Bootstrap styling to the issue detail page for layout consistency.
- Add a Markdown preview/editor experience with two modes:
  - **Source-edit mode** (always available)
  - **Optional WYSIWYG preview or editing mode**
- Preserve good LLM/text-edit interop by keeping raw Markdown accessible.

---

## 🧱 Implementation Plan

### 1. **Wrap layout in Bootstrap container**

- Add `.container`, `.mb-3`, etc., to existing form elements.
- Use `.form-control` on the `<textarea>`.
- Label + status field using `.form-label`, `.form-select`, etc.

### 2. **Add Markdown editing/preview modes**

- UI should offer tabbed or toggle controls to switch between:
  - Raw Markdown source (textarea)
  - Rendered preview (read-only)
  - Optional WYSIWYG editor (if implemented)
- Options:
  - For preview only: [marked.js](https://github.com/markedjs/marked)
  - For WYSIWYG: [Toast UI Editor](https://ui.toast.com/tui-editor), [EasyMDE](https://github.com/Ionaru/easy-markdown-editor), or [TipTap](https://tiptap.dev)

### 3. **Script logic**

- Toggle between modes (edit, preview, WYSIWYG) with Bootstrap tabs or buttons.
- Keep a single Markdown source of truth (sync between modes as needed).
- Sanitize rendered HTML (e.g., with [DOMPurify](https://github.com/cure53/DOMPurify)).

---

## ✅ Developer Mode & LLM-Friendly

- Source always editable in a real `<textarea>`.
- WYSIWYG is optional and should interoperate with raw Markdown.
- Markdown format remains the canonical form for saving.

### Comments

2025.07.21 2028

Seems like this is all good.  Added the font-awesome link and a sync back to the raw view.

---

2025.07.21 2033

Only sync wysiwyg to raw on save if wysiwyg is active.