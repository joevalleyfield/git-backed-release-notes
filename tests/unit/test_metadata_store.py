"""Coverage for commit metadata store helpers."""

from pathlib import Path

import pandas as pd

from git_release_notes.utils.metadata_store import (
    DataFrameCommitMetadataStore,
    SpreadsheetCommitMetadataStore,
)


def _write_csv(path: Path, rows: list[dict]) -> None:
    pd.DataFrame(rows).to_csv(path, index=False)


def _write_xlsx(path: Path, rows: list[dict]) -> None:
    pd.DataFrame(rows).to_excel(path, index=False)


def test_dataframe_store_shas_for_issue(tmp_path):
    csv_path = tmp_path / "metadata.csv"
    _write_csv(
        csv_path,
        [
            {"sha": "aaa111", "issue": "alpha", "release": ""},
            {"sha": "bbb222", "issue": "", "release": ""},
            {"sha": "ccc333", "issue": "alpha", "release": ""},
        ],
    )

    store = DataFrameCommitMetadataStore(csv_path)

    assert store.shas_for_issue("alpha") == ["aaa111", "ccc333"]
    assert store.shas_for_issue("missing") == []


def test_spreadsheet_store_shas_for_issue(tmp_path):
    xlsx_path = tmp_path / "metadata.xlsx"
    initial_rows = [
        {"sha": "aaa111", "issue": "alpha", "release": ""},
        {"sha": "bbb222", "issue": "beta", "release": ""},
    ]
    _write_xlsx(xlsx_path, initial_rows)

    store = SpreadsheetCommitMetadataStore(pd.DataFrame(initial_rows), xlsx_path)

    assert store.shas_for_issue("beta") == ["bbb222"]
    assert store.shas_for_issue("other") == []


def test_dataframe_store_reload_refreshes_from_disk(tmp_path):
    csv_path = tmp_path / "metadata.csv"
    _write_csv(
        csv_path,
        [
            {"sha": "aaa111", "issue": "alpha", "release": ""},
            {"sha": "bbb222", "issue": "", "release": ""},
        ],
    )

    store = DataFrameCommitMetadataStore(csv_path)
    assert store.shas_for_issue("alpha") == ["aaa111"]

    _write_csv(
        csv_path,
        [
            {"sha": "ccc333", "issue": "gamma", "release": ""},
        ],
    )

    store.reload()

    assert store.shas_for_issue("alpha") == []
    assert store.shas_for_issue("gamma") == ["ccc333"]


def test_spreadsheet_store_reload_reads_updated_workbook(tmp_path):
    xlsx_path = tmp_path / "metadata.xlsx"
    initial_rows = [
        {"sha": "aaa111", "issue": "alpha", "release": ""},
        {"sha": "bbb222", "issue": "", "release": ""},
    ]
    _write_xlsx(xlsx_path, initial_rows)

    store = SpreadsheetCommitMetadataStore(pd.DataFrame(initial_rows), xlsx_path)
    assert store.shas_for_issue("alpha") == ["aaa111"]

    updated_rows = [
        {"sha": "ddd444", "issue": "delta", "release": ""},
    ]
    _write_xlsx(xlsx_path, updated_rows)

    store.reload()

    assert store.shas_for_issue("alpha") == []
    assert store.shas_for_issue("delta") == ["ddd444"]
