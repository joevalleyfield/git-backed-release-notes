#!/usr/bin/env bash
set -euo pipefail

# List all mutable courier refs on origin
git ls-remote origin "refs/jj/mutable/*" | awk '{print $2}' | sed 's#refs/jj/mutable/##'