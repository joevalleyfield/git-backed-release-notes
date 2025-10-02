# utils/metadata_store.py
# utils/metadata_store.py

from abc import ABC, abstractmethod
from pathlib import Path
import logging

import pandas as pd

from .data import atomic_save_excel, get_row_index_by_sha

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class CommitMetadataStore(ABC):
    """Abstract base class for reading and writing commit metadata (e.g. issue, release)."""
    @abstractmethod
    def get_metadata_df(self) -> pd.DataFrame:
        """
        Return the current metadata DataFrame with at least columns:
        ['sha', 'issue', 'release'] (missing ones are okay; they’ll be treated as empty).
        """
        ...

    @abstractmethod
    def limits_commit_set(self) -> bool:
        """
        If True, this store’s spreadsheet/dataframe defines the exact set/order of SHAs
        the UI should render. If False, show all commits from Git and just merge fields.
        """
        ...

    @abstractmethod
    def get_row(self, sha: str) -> dict | None:
        ...

    @abstractmethod
    def set_issue(self, sha: str, issue: str) -> None:
        ...

    @abstractmethod
    def set_release(self, sha: str, release: str) -> None:
        ...

    @abstractmethod
    def shas_for_issue(self, issue: str) -> list[str]:
        """Return all commit SHAs linked to the given issue slug."""
        ...

    def reload(self) -> None:
        """Optional no-op: stores may override to refresh from their backing file."""
        pass

    def save(self) -> None:
        """Optional no-op for stores that persist immediately."""
        pass


class SpreadsheetCommitMetadataStore(CommitMetadataStore):
    """Backs commit metadata with a spreadsheet DataFrame and Excel path."""

    def __init__(self, df: pd.DataFrame, excel_path: Path):
        self._df = df
        self.excel_path = Path(excel_path)

    def _ensure_row(self, sha: str):
        """Ensure that a row exists for the given SHA; insert one if missing."""
        if sha not in self._df["sha"].values:
            self._df = pd.concat([
                self._df,
                pd.DataFrame([{"sha": sha, "issue": "", "release": ""}])
            ], ignore_index=True)

    def get_metadata_df(self) -> pd.DataFrame:
        return self._df.fillna("")

    def get_row(self, sha: str) -> dict | None:
        match = self._df[self._df["sha"] == sha]
        if not match.empty:
            return match.iloc[0].to_dict()
        return None

    def limits_commit_set(self) -> bool:
        return True
    
    def reload(self) -> None:
        try:
            # Assumes the sheet written by `atomic_save_excel` has the expected columns
            self._df = pd.read_excel(self.excel_path)
        except Exception as e:
            logger.warning("SpreadsheetCommitMetadataStore reload failed: %s", e)

    def set_issue(self, sha: str, value: str):
        self._ensure_row(sha)
        self._df.loc[self._df["sha"] == sha, "issue"] = value

    def set_release(self, sha: str, value: str):
        self._ensure_row(sha)
        self._df.loc[self._df["sha"] == sha, "release"] = value

    def save(self) -> None:
        atomic_save_excel(self._df, self.excel_path)

    def shas_for_issue(self, issue: str) -> list[str]:
        matches = self._df[self._df["issue"] == issue]
        return matches["sha"].tolist()


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

    def get_metadata_df(self) -> pd.DataFrame:
        return self.df.fillna("")

    def get_row(self, sha: str) -> dict | None:
        match = self.df[self.df["sha"] == sha]
        if not match.empty:
            return match.iloc[0].to_dict()
        return None

    def limits_commit_set(self) -> bool:
        return False

    def reload(self) -> None:
        if self.path.exists():
            try:
                self.df = pd.read_csv(self.path)
            except Exception as e:
                logger.warning("DataFrameCommitMetadataStore reload failed: %s", e)

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

    def shas_for_issue(self, issue: str) -> list[str]:
        matches = self.df[self.df["issue"] == issue]
        return matches["sha"].tolist()
