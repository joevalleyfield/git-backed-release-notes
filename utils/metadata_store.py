# utils/metadata_store.py
# utils/metadata_store.py

from abc import ABC, abstractmethod
from pathlib import Path
import logging
import pandas as pd

from utils.data import atomic_save_excel, get_row_index_by_sha

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class CommitMetadataStore(ABC):
    """Abstract base class for reading and writing commit metadata (e.g. issue, release)."""

    @abstractmethod
    def set_issue(self, sha: str, issue: str) -> None:
        ...

    @abstractmethod
    def set_release(self, sha: str, release: str) -> None:
        ...

    def save(self) -> None:
        """Optional no-op for stores that persist immediately."""
        pass


class SpreadsheetCommitMetadataStore(CommitMetadataStore):
    """Backs commit metadata with a spreadsheet DataFrame and Excel path."""

    def __init__(self, df: pd.DataFrame, excel_path: Path):
        self.df = df
        self.excel_path = Path(excel_path)

    def set_issue(self, sha: str, issue: str) -> None:
        row_idx = get_row_index_by_sha(self.df, sha)
        if row_idx is None:
            raise KeyError(f"No spreadsheet row found for commit {sha}")
        self.df.at[row_idx, "issue"] = issue

    def set_release(self, sha: str, release: str) -> None:
        row_idx = get_row_index_by_sha(self.df, sha)
        if row_idx is None:
            raise KeyError(f"No spreadsheet row found for commit {sha}")
        self.df.at[row_idx, "release"] = release

    def save(self) -> None:
        atomic_save_excel(self.df, self.excel_path)


class DataFrameCommitMetadataStore(CommitMetadataStore):
    """
    File-backed store that keeps commit metadata in a simple CSV-based DataFrame.
    Used when no spreadsheet is present.
    """

    def __init__(self, csv_path: Path = Path("git-view.metadata.csv")):
        self.path = Path(csv_path)
        if self.path.exists():
            self.df = pd.read_csv(self.path)
        else:
            self.df = pd.DataFrame(columns=["sha", "issue", "release"])

    def set_issue(self, sha: str, issue: str) -> None:
        row_idx = get_row_index_by_sha(self.df, sha)
        if row_idx is None:
            self.df.loc[len(self.df)] = [sha, issue, ""]
        else:
            self.df.at[row_idx, "issue"] = issue

    def set_release(self, sha: str, release: str) -> None:
        row_idx = get_row_index_by_sha(self.df, sha)
        if row_idx is None:
            self.df.loc[len(self.df)] = [sha, "", release]
        else:
            self.df.at[row_idx, "release"] = release

    def save(self) -> None:
        self.df.to_csv(self.path, index=False)
