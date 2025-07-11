# Remove Self-Following Tags from `Follows:` Output

Currently, the `Follows:` line is displayed even when the commit being viewed is directly tagged.

This is redundant — the `git describe` output (shown in italics) already makes it clear that the commit is the target of the tag.

## Expected Behavior

If the result of `git describe` is just the tag name (i.e. no `-<count>-g<sha>` suffix), we should skip rendering the `Follows:` line entirely.

## Suggested Implementation

- In `find_follows_tag()`, if `count == 0`, skip returning a `SimpleNamespace`
- In the template, omit the `Follows:` block if `follows is None`

## Related Features

- This supports the goal of cleaner, non-redundant commit detail views
- Builds on previous improvements to `git describe` parsing and logging

## Resolution

- If a commit is directly tagged (`count == 0`), the Follows line is omitted
- The `git describe` string is still shown in italics as context
