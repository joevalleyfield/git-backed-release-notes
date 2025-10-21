#!/usr/bin/env bash
# Source this file (e.g., `source scripts/aliases.sh`) to expose project helpers.

if [ -n "${BASH_VERSION:-}" ]; then
    shopt -s expand_aliases
fi

export UV_CACHE_DIR=${UV_CACHE_DIR:-.uv-cache}

alias ruff-run="$(pwd)/scripts/run-ruff.sh"
alias black-run="$(pwd)/scripts/run-black.sh"
alias mypy-run="$(pwd)/scripts/run-mypy.sh"
alias pre-commit-run="$(pwd)/scripts/run-precommit.sh"

source <(./scripts/jj-gen-aliases.sh)
