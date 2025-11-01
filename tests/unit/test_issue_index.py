from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from src.git_release_notes.utils.issue_index import collect_issue_index_rows, group_releases
from src.git_release_notes.utils.metadata_store import DataFrameCommitMetadataStore


def write_csv(path: Path, header: str, rows: list[str]) -> None:
    contents = "\n".join([header, *rows]) + "\n"
    path.write_text(contents, encoding="utf-8")


def test_collect_issue_index_rows_prefers_front_matter_and_metadata(tmp_path):
    repo_root = tmp_path
    issues_root = repo_root / "issues"
    open_dir = issues_root / "open"
    closed_dir = issues_root / "closed"
    open_dir.mkdir(parents=True)
    closed_dir.mkdir()

    (open_dir / "progressive-index.md").write_text(
        "\n".join(
            [
                "release: release-a",
                "last_updated: 2024-02-14",
                "",
                "# Progressive Index",
                "body",
            ]
        ),
        encoding="utf-8",
    )
    (closed_dir / "historical-cleanup.md").write_text(
        "\n".join(
            [
                "last_updated: 2024-01-29",
                "",
                "# Historical cleanup",
                "body",
            ]
        ),
        encoding="utf-8",
    )

    metadata_path = repo_root / "git-view.metadata.csv"
    write_csv(
        metadata_path,
        "sha,issue,release",
        [
            "sha123,progressive-index,release-a",
            "sha999,historical-cleanup,release-b",
        ],
    )

    commits_path = repo_root / "commits.csv"
    write_csv(
        commits_path,
        "sha,summary,issue,landed_at",
        [
            "sha123,Progressive Index,progressive-index,2024-02-13T10:00:00+00:00",
            "sha456,Historical Cleanup,historical-cleanup,2024-01-31 08:15",
        ],
    )

    store = DataFrameCommitMetadataStore(metadata_path)
    rows = collect_issue_index_rows(repo_root, issues_root, store)

    assert len(rows) == 2
    rows_by_slug = {row.slug: row for row in rows}

    progressive = rows_by_slug["progressive-index"]
    assert progressive.status == "open"
    assert progressive.release == "release-a"
    assert progressive.last_updated == datetime(2024, 2, 14, tzinfo=timezone.utc)
    assert progressive.landed_at == datetime(2024, 2, 13, 10, 0, tzinfo=timezone.utc)
    assert set(progressive.commit_shas) == {"sha123"}

    historical = rows_by_slug["historical-cleanup"]
    assert historical.status == "closed"
    # release inferred from metadata CSV
    assert historical.release == "release-b"
    assert historical.last_updated == datetime(2024, 1, 29, tzinfo=timezone.utc)
    assert historical.landed_at == datetime(2024, 1, 31, 8, 15, tzinfo=timezone.utc)
    assert set(historical.commit_shas) == {"sha456", "sha999"}


def test_group_releases_sorts_and_deduplicates(tmp_path):
    repo_root = tmp_path
    issues_root = repo_root / "issues"
    (issues_root / "open").mkdir(parents=True)
    (issues_root / "closed").mkdir()

    (issues_root / "open" / "alpha.md").write_text(
        "release: release-x\nlast_updated: 2024-01-01\n\n", encoding="utf-8"
    )
    (issues_root / "closed" / "beta.md").write_text("last_updated: 2024-01-02\n\n", encoding="utf-8")

    metadata_path = repo_root / "git-view.metadata.csv"
    write_csv(metadata_path, "sha,issue,release", ["sha1,alpha,release-x", "sha2,beta,release-y"])
    write_csv(repo_root / "commits.csv", "sha,summary,issue,landed_at", ["sha1,Alpha Work,alpha,2024-01-03"])

    store = DataFrameCommitMetadataStore(metadata_path)
    rows = collect_issue_index_rows(repo_root, issues_root, store)

    assert group_releases(rows) == ["release-x", "release-y"]
