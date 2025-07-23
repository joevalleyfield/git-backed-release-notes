# Edit closed issues and redirect on success

The `IssueUpdateHandler` currently has two limitations:

- It only updates issues in the `open/` directory.
- It responds with `"OK"` instead of redirecting after a successful update.

## Tasks

- [ ] Support editing issues in either `open/` or `closed/`
- [ ] Return 404 only if the issue does not exist in either location
- [ ] Redirect to the issue page (`/issue/<slug>`) after a successful update
