"""Compatibility shim while the CLI transitions to the packaged entry point."""

from __future__ import annotations

import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent / "src"
if SRC_DIR.exists():
    sys.path.insert(0, str(SRC_DIR))

from git_release_notes.__main__ import main  # noqa: E402

if __name__ == "__main__":
    main()
