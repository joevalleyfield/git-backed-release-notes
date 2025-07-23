# Edit closed issues and redirect on success

The `IssueUpdateHandler` previously had two limitations:

- It only updated issues in the `open/` directory.
- It responded with `"OK"` instead of redirecting after a successful update.

These behaviors have been addressed:

- ✅ Editing now works for both `open/` and `closed/` issues
- ✅ A redirect to `/issue/<slug>` occurs on successful update
- ✅ A new Behave scenario verifies edits to closed issues succeed

The `find_issue_file()` helper was introduced to share lookup logic between `IssueDetailHandler` and `IssueUpdateHandler`.
