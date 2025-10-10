#!/usr/bin/env bash
set -euo pipefail

UV_CACHE_DIR="${UV_CACHE_DIR:-.uv-cache}" exec uv tool run pre-commit "$@"
