#!/usr/bin/env bash
set -euo pipefail

usage() {
    cat <<'USAGE'
Usage: scripts/ci-local.sh [--locked] [--skip-behave] [--skip-playwright-install]

Provision a throwaway virtual environment, install test extras, then run pytest and Behave.
Options:
  --locked  Install from requirements-dev.lock via uv to mirror CI.
  --skip-behave  Skip running Behave scenarios (useful while debugging pytest failures).
  --skip-playwright-install  Assume Playwright browsers are already installed.
USAGE
}

SKIP_BEHAVE=0
SKIP_PLAYWRIGHT_INSTALL=0
USE_LOCKED=0
while (($#)); do
    case "$1" in
        --locked)
            USE_LOCKED=1
            shift
            ;;
        --skip-behave)
            SKIP_BEHAVE=1
            shift
            ;;
        --skip-playwright-install)
            SKIP_PLAYWRIGHT_INSTALL=1
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            printf 'Unknown argument: %s\n\n' "$1" >&2
            usage >&2
            exit 1
            ;;
    esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
VENV_DIR="${REPO_ROOT}/.venv-ci-local"
PYTHON_BIN="${VENV_DIR}/bin/python"

if command -v uv >/dev/null 2>&1; then
    UV_AVAILABLE=1
else
    UV_AVAILABLE=0
fi

if [ "${USE_LOCKED}" -eq 1 ] && [ "${UV_AVAILABLE}" -ne 1 ]; then
    echo "[ci-local] --locked requires uv to be installed" >&2
    exit 2
fi

if [ ! -d "${VENV_DIR}" ]; then
    if [ "${UV_AVAILABLE}" -eq 1 ]; then
        echo "[ci-local] Creating virtualenv with uv at ${VENV_DIR}"
        uv venv "${VENV_DIR}"
    else
        echo "[ci-local] Creating virtualenv with python -m venv at ${VENV_DIR}"
        python3 -m venv "${VENV_DIR}"
    fi
fi

# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"

cd "${REPO_ROOT}"

if [ "${UV_AVAILABLE}" -eq 1 ]; then
    if [ "${USE_LOCKED}" -eq 1 ]; then
        if [ ! -f "${REPO_ROOT}/requirements-dev.lock" ]; then
            echo "[ci-local] requirements-dev.lock is missing; run 'uv pip compile ... --extra test' first" >&2
            exit 2
        fi

        echo "[ci-local] Syncing dependencies from requirements-dev.lock"
        uv pip sync --python "${PYTHON_BIN}" requirements-dev.lock

        echo "[ci-local] Installing project in editable mode without dependencies"
        uv pip install --python "${PYTHON_BIN}" --no-deps -e .
    else
        echo "[ci-local] Installing project in editable mode via uv"
        uv pip install --python "${PYTHON_BIN}" --upgrade pip setuptools wheel
        uv pip install --python "${PYTHON_BIN}" -e ".[test]"
    fi
else
    echo "[ci-local] Installing project in editable mode via pip"
    python -m pip install --upgrade pip setuptools wheel
    pip install -e ".[test]"
fi

if ! command -v ruff >/dev/null 2>&1; then
    echo "[ci-local] Ruff is required for linting; ensure test extras are installed" >&2
    exit 3
fi

echo "[ci-local] Running ruff lint"
ruff check .

echo "[ci-local] Running pytest"
pytest --maxfail=1 --disable-warnings

if [ "$SKIP_BEHAVE" -ne 1 ]; then
    if [ "$SKIP_PLAYWRIGHT_INSTALL" -ne 1 ]; then
        echo "[ci-local] Ensuring Playwright browsers are installed"
        python -m playwright install --with-deps chromium >/dev/null
    else
        echo "[ci-local] Skipping Playwright browser installation"
    fi

    echo "[ci-local] Running Behave (full suite)"
    behave
else
    echo "[ci-local] Skipping Behave as requested"
fi
