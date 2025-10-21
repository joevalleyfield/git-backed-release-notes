#!/usr/bin/env bash
set -euo pipefail

self="$(basename "$0")"

# Generate aliases for all jj-*.sh scripts except this one
for script in "$(dirname "$0")"/jj-*.sh; do
  name=$(basename "$script")
  [ "$name" = "$self" ] && continue
  alias_name="${name%.sh}"
  echo "alias $alias_name=\"$(pwd)/scripts/$name\""
done