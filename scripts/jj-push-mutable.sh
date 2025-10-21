#!/usr/bin/env bash
set -euo pipefail

arg="${1:?usage: jj-push-mutable <topic-or-change-id>}"

# Resolve argument: if it matches a change, use its full change_id; else use literal
if change_id=$(jj log -r "$arg" --no-graph --template 'change_id' 2>/dev/null); then
    topic="$change_id"
else
    topic="$arg"
    change_id=$(jj log -r @ --no-graph --template 'change_id')
fi

commit_id=$(jj log -r "$arg" --no-graph --template 'commit_id' 2>/dev/null || jj log -r @ --no-graph --template 'commit_id')

ref="refs/jj/mutable/$topic"

# Write and push
git update-ref "$ref" "$commit_id"
git push origin "$ref:$ref" --force

echo "Pushed mutable change @$change_id ($commit_id) to $ref"