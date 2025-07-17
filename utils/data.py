"""
Spreadsheet utility functions for reading and updating commit metadata.

Includes:
- get_row_index_by_sha: find a row in the DataFrame by commit SHA
- atomic_save_excel: write updates safely using a temporary file
"""

import os
from pathlib import Path
from tempfile import NamedTemporaryFile

import pandas as pd


def get_row_index_by_sha(df: pd.DataFrame, sha: str) -> int | None:
    """
    Return the index of the commit with the given SHA, or None if not found.
    """
    matches = df[df["sha"] == sha]
    if not matches.empty:
        return matches.index[0]
    return None


def atomic_save_excel(df: pd.DataFrame, path: Path):
    """
    Atomically save a DataFrame to an Excel file.

    Writes the DataFrame to a temporary file in the same directory as `path`, then
    replaces the original file using `os.replace()` for atomicity.

    By creating the temp file in the target directory, we ensure it's on the same
    filesystem, avoiding issues with cross-device replacements. Symlinked paths or
    nonstandard mounts could still violate this assumption.
    """
    with NamedTemporaryFile("wb", dir=path.parent, delete=False) as tmp:
        tmp_path = Path(tmp.name)
        df.to_excel(tmp_path, index=False)
    os.replace(tmp_path, path)  # Atomic if on same filesystem
