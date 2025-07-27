# Feature: Auto-open Browser on Launch

## Motivation

When running the app locally with `python app.py`, it would be helpful if the browser opened automatically. This makes manual testing and exploration more seamless, especially for new users or during development.

## Implementation

- After the app binds to the selected port, the server sleeps briefly and then opens the default browser to `http://localhost:<port>`
- Includes a `--no-browser` flag to suppress this behavior when running in headless environments (CI, containers, etc.)
- Uses Python’s built-in `webbrowser` module

## Status

✅ Implemented and tested in local dev mode  
✅ Dynamically respects CLI port  
✅ Gated by `--no-browser`
