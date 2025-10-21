#!/usr/bin/env bash
set -euo pipefail

arg="${1:?usage: jj-pull-mutable <topic-or-change-id>}"
ref="refs/jj/mutable/$arg"

# Fetch the courier ref
git fetch origin "$ref:$ref"

# Verify the ref exists locally
if ! git show-ref --verify --quiet "$ref"; then
    echo "Error: $ref not found locally after fetch" >&2
    exit 1
fi

# Get the change_id from that commit
change_id=$(jj log -r "git_ref(\"$ref\")" --no-graph --template 'change_id' 2>/dev/null || true)

echo "Fetched $ref (change_id=$change_id)"

# Check it out
jj checkout "git_ref(\"$ref\")"