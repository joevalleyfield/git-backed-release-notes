# Jujutsu (jj) Primer

This document is a crash course for using [Jujutsu](https://github.com/jj-vcs/jj) as a Git-compatible DVCS in this project.  
It focuses on the *mental model*, *basic commands*, and JJ-specific tricks we actually use.

---

## Mental Model
- **Changes, not commits**  
  A *change* is the unit of history. A change can be rewritten until you publish it. Commits are just snapshots JJ keeps behind the scenes.

- **Mutable vs Immutable**  
  - Mutable = drafts (safe to rewrite, squash, split, rebase).  
  - Immutable = published changes (main, release/*). Don’t rewrite except with `--ignore-immutable`.

- **Operation log (oplog)**  
  Every edit you make to history is recorded in the oplog. You can `jj op log`, `jj op undo`, or `jj op restore` to move backward/forward in time safely.

- **Git interoperability**  
  Colocated repos share object storage with Git. JJ writes helper refs under `refs/jj/` and can push/pull just like Git.

---

## Core Commands

### Working with changes
```bash
jj status                  # show working copy vs current change
jj log -r all()            # show history DAG
jj new                     # create a new change
jj describe -m "feat: ..." # set or update message for current change
jj squash                  # combine with parent
jj split                   # break change into multiple smaller ones
jj rebase -s @ -d main     # rebase current change onto main
jj bookmark set feature/foo  # name a change for easy reference
```

### Publishing and syncing
```bash
jj git fetch
jj git push
```

---

## Describing Intention First

One of JJ’s strengths is recording intent before doing the work.  

```bash
jj new
jj describe --stdin <<'EOF'
fix: remove stray update_foo.sh

This was accidentally committed in a previous change. See issue
`issues/closed/move-entry-point-to-git-release-notes-main.md`.
EOF

rm update_foo.sh
jj status   # JJ already captured the deletion in the working copy
```

---

## Template Cheatsheet

JJ templates let you control output for `jj log`, `jj show`, etc.  
Common fields:

- `{commit_id}` — full commit SHA  
- `{commit_id.short()}` — short SHA  
- `{change_id}` — JJ’s stable ID for the change  
- `{description}` — commit message subject/body  
- `{author}` — author info  
- `{branches}` — bookmarks pointing here  
- `{tags}` — Git tags pointing here  

### Examples
```bash
# Compact log with both Git and JJ IDs
jj log -r all() -T '{commit_id.short()} {change_id.short()} {branches} {description.first_line()}'

# Show change ID and author
jj show -r @ -T 'change {change_id.short()} by {author}'
```

---

## Git → JJ Mental Model Table

| **Intent / Action**                          | **Git mindset**                                                                 | **JJ mindset**                                                                                 |
|----------------------------------------------|----------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------|
| “I want to save my work in progress.”        | `git commit` creates an immutable snapshot. To change it, you amend or make fixups.| `jj new` creates a **change** (mutable). Every edit updates that same change until you publish.|
| “I want to edit a commit I just made.”       | `git commit --amend`, or interactive rebase. Feels like rewriting history.        | `jj describe` or just edit files: JJ rewrites the change by default. No danger until published. |
| “I want to combine or split commits.”        | `git rebase -i` with squash/fixup/split.                                         | `jj squash` and `jj split` are first-class commands. History manipulation is normal.            |
| “I want to share my feature branch.”         | Create a branch (`git checkout -b feature/foo`), push to remote.                 | Set a bookmark (`jj bookmark set feature/foo`). Bookmarks are movable pointers to changes.       |
| “I want to land on main.”                    | Merge or rebase branch into `main`.                                              | Rebase your mutable change onto `main`, then advance the `main` bookmark. `main` is immutable.  |
| “I want to fix a mistake in published history.” | Rewrite with `git rebase --onto` or graft (dangerous).                            | You *don’t*. Immutable is sacred. Make a new change on top, or branch from the oops and merge fix.|
| “I want to see what happened recently.”      | `git log` (commits, immutable).                                                  | `jj log` (changes). Remember: changes may evolve, and the op-log tracks every rewrite.           |
| “I want to undo a rebase or history edit.”   | Pray the reflog has it: `git reflog`.                                            | Guaranteed: `jj op log` and `jj op restore` let you roll back to any prior state.                |
| “I want to ignore junk files.”               | `.gitignore`.                                                                    | `.jjignore` (shares syntax with `.gitignore`).                                                   |
| “I want to push/pull to GitHub.”             | `git push`, `git fetch`.                                                         | `jj git push`, `jj git fetch`. Git refs and JJ bookmarks sync transparently.                     |

### Fuzzy Lines

- **Commit vs Change**  
  In Git: one commit = one immutable object.  
  In JJ: one change = many evolving commits until published.  

- **Branch vs Bookmark**  
  In Git: branch = named ref that moves with new commits.  
  In JJ: bookmark = pointer to a change. Bookmarks can move, but mutability is tied to *what the change is*, not the bookmark itself.  

- **History vs Operation Log**  
  In Git: `git log` shows commits; reflog is separate, lossy.  
  In JJ: `jj log` shows changes; `jj op log` shows how you got there. Both are first-class.  

---

## Further Reading
- [JJ Official Docs](https://jj-vcs.github.io/jj/latest/)  
- `jj help` and `jj help templates`
