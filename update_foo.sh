# Work on the commit we want to fix
jj edit 1a373327569292804ce667983d72914e41d35733

# Define the bad commit (before repair) so we can restore edited content
BAD=1a373327569292804ce667983d72914e41d35733
PARENT='parents()'

# ---- Entry point ----
jj restore --from $PARENT -- src/git_release_notes/__main__.py
jj mv app.py src/git_release_notes/__main__.py
jj restore --from $BAD -- src/git_release_notes/__main__.py

# ---- Handlers ----
for f in commit.py issue.py main.py update.py; do
  jj restore --from $PARENT -- src/git_release_notes/handlers/$f
  jj mv handlers/$f src/git_release_notes/handlers/$f
  jj restore --from $BAD -- src/git_release_notes/handlers/$f
done

# ---- Templates ----
for f in commit.html index.html issue.html; do
  jj restore --from $PARENT -- src/git_release_notes/templates/$f
  jj mv templates/$f src/git_release_notes/templates/$f
  jj restore --from $BAD -- src/git_release_notes/templates/$f
done

# ---- Utils ----
for f in commit_parsing.py data.py git.py issues.py metadata_store.py; do
  jj restore --from $PARENT -- src/git_release_notes/utils/$f
  jj mv utils/$f src/git_release_notes/utils/$f
  jj restore --from $BAD -- src/git_release_notes/utils/$f
done

# Finalize the commit
# jj commit -m "feat: migrate entry point into src layout (properly record moves)"
