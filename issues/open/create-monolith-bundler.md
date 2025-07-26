# Tool: Create Monolith Bundler for Git Viewer

## Motivation

Now that the app is modularized into `handlers/` and `utils/`, it's helpful to offer a bundler that reassembles a single-file version (`git_viewer_monolith.py`) for portability or downstream integration.

## Goals

- Implement `tools/bundle.py` as described in `refactor-app-for-modularization.md`
- Maintain an explicit, ordered list of module files
- Emit `# === filename ===` boundaries for readability
- Output to `git_viewer_monolith.py` in the project root

## Future Considerations

- Add support for CLI invocation: `python tools/bundle.py`
- Consider pre-processing or stripping tests/debug sections in prod bundles
