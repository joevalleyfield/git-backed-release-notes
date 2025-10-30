# 🚦 Issue: Add Graceful Shutdown on Ctrl+C

```yaml
tags: [server, shutdown, tornado]
status: open
```

## Motivation

Running `python -m git_release_notes` responds to Ctrl+C with an abrupt
`KeyboardInterrupt` trace. The Tornado I/O loop keeps references alive and the
process exits without giving request handlers or cleanup hooks the chance to run.

## Goals

- Stop the Tornado `IOLoop` when SIGINT or SIGTERM is received.
- Confirm the CLI exits without printing a traceback in normal shutdown paths.
- Ensure tests cover the signal handling behavior so regressions are caught.

## Open Questions

- Do we need to surface a shutdown message to the CLI user, or keep the current
  silent exit?

