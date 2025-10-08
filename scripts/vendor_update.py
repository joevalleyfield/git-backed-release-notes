#!/usr/bin/env python3
"""Download and pin third-party frontend assets into the vendor directory."""

from __future__ import annotations

import argparse
import base64
import hashlib
import io
import json
import sys
import tarfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List
from urllib.error import URLError, HTTPError
from urllib.request import urlopen

PROJECT_ROOT = Path(__file__).resolve().parent.parent
VENDOR_DIR = PROJECT_ROOT / "src" / "git_release_notes" / "static" / "vendor"
MANIFEST_PATH = VENDOR_DIR / "manifest.json"


@dataclass
class AssetFile:
    """Represents a single vendored file to be written."""

    url: str
    dest: Path
    member: str | None = None  # Only used for tarball sources


@dataclass
class DownloadPlan:
    """High level plan for downloading one or more asset files."""

    source_url: str
    files: List[AssetFile]
    is_tarball: bool = False


ASSETS: List[DownloadPlan] = [
    DownloadPlan(
        source_url="https://cdn.jsdelivr.net/npm/bootstrap@5.3.7/dist/css/bootstrap.min.css",
        files=[AssetFile(url="https://cdn.jsdelivr.net/npm/bootstrap@5.3.7/dist/css/bootstrap.min.css",
                         dest=VENDOR_DIR / "bootstrap-5.3.7.min.css")],
    ),
    DownloadPlan(
        source_url="https://cdn.jsdelivr.net/npm/bootstrap@5.3.7/dist/js/bootstrap.bundle.min.js",
        files=[AssetFile(url="https://cdn.jsdelivr.net/npm/bootstrap@5.3.7/dist/js/bootstrap.bundle.min.js",
                         dest=VENDOR_DIR / "bootstrap-5.3.7.bundle.min.js")],
    ),
    DownloadPlan(
        source_url="https://cdn.jsdelivr.net/npm/diff2html@3.4.52/bundles/css/diff2html.min.css",
        files=[AssetFile(url="https://cdn.jsdelivr.net/npm/diff2html@3.4.52/bundles/css/diff2html.min.css",
                         dest=VENDOR_DIR / "diff2html-3.4.52.min.css")],
    ),
    DownloadPlan(
        source_url="https://cdn.jsdelivr.net/npm/diff2html@3.4.52/bundles/js/diff2html-ui.min.js",
        files=[AssetFile(url="https://cdn.jsdelivr.net/npm/diff2html@3.4.52/bundles/js/diff2html-ui.min.js",
                         dest=VENDOR_DIR / "diff2html-ui-3.4.52.min.js")],
    ),
    DownloadPlan(
        source_url="https://cdn.jsdelivr.net/npm/easymde@2.20.0/dist/easymde.min.css",
        files=[AssetFile(url="https://cdn.jsdelivr.net/npm/easymde@2.20.0/dist/easymde.min.css",
                         dest=VENDOR_DIR / "easymde-2.20.0.min.css")],
    ),
    DownloadPlan(
        source_url="https://cdn.jsdelivr.net/npm/easymde@2.20.0/dist/easymde.min.js",
        files=[AssetFile(url="https://cdn.jsdelivr.net/npm/easymde@2.20.0/dist/easymde.min.js",
                         dest=VENDOR_DIR / "easymde-2.20.0.min.js")],
    ),
    DownloadPlan(
        source_url="https://cdn.jsdelivr.net/npm/marked@15.0.12/marked.min.js",
        files=[AssetFile(url="https://cdn.jsdelivr.net/npm/marked@15.0.12/marked.min.js",
                         dest=VENDOR_DIR / "marked-15.0.12.min.js")],
    ),
    DownloadPlan(
        source_url="https://cdn.jsdelivr.net/npm/dompurify@3.1.3/dist/purify.min.js",
        files=[AssetFile(url="https://cdn.jsdelivr.net/npm/dompurify@3.1.3/dist/purify.min.js",
                         dest=VENDOR_DIR / "dompurify-3.1.3.min.js")],
    ),
    DownloadPlan(
        source_url="https://registry.npmjs.org/@fortawesome/fontawesome-free/-/fontawesome-free-6.5.2.tgz",
        is_tarball=True,
        files=[
            AssetFile(
                url="https://registry.npmjs.org/@fortawesome/fontawesome-free/-/fontawesome-free-6.5.2.tgz",
                dest=VENDOR_DIR / "fontawesome-free-6.5.2" / "css" / "all.min.css",
                member="package/css/all.min.css",
            ),
        ],
    ),
]

# Additional webfont members for Font Awesome tarball
FONT_AWESOME_WEBFONTS = [
    "package/webfonts/fa-brands-400.ttf",
    "package/webfonts/fa-brands-400.woff2",
    "package/webfonts/fa-regular-400.ttf",
    "package/webfonts/fa-regular-400.woff2",
    "package/webfonts/fa-solid-900.ttf",
    "package/webfonts/fa-solid-900.woff2",
    "package/webfonts/fa-v4compatibility.ttf",
    "package/webfonts/fa-v4compatibility.woff2",
]

for member in FONT_AWESOME_WEBFONTS:
    ASSETS[-1].files.append(
        AssetFile(
            url=ASSETS[-1].source_url,
            dest=VENDOR_DIR / "fontawesome-free-6.5.2" / "webfonts" / Path(member).name,
            member=member,
        )
    )


def fetch_bytes(url: str) -> bytes:
    """Retrieve bytes from the given URL."""

    with urlopen(url) as response:
        return response.read()


def ensure_directory(path: Path) -> None:
    """Ensure the destination directory exists."""

    path.parent.mkdir(parents=True, exist_ok=True)


def write_file(path: Path, data: bytes) -> None:
    ensure_directory(path)
    path.write_bytes(data)


def download_file(plan: DownloadPlan, asset_file: AssetFile, *, force: bool) -> None:
    if not force and asset_file.dest.exists():
        print(f"[skip] {asset_file.dest.relative_to(VENDOR_DIR)} (already exists)")
        return

    print(f"[fetch] {asset_file.url}")
    data = fetch_bytes(asset_file.url)
    write_file(asset_file.dest, data)


def download_tarball(plan: DownloadPlan, *, force: bool) -> None:
    if not force and all(af.dest.exists() for af in plan.files):
        print("[skip] fontawesome tarball (all files already present)")
        return

    print(f"[fetch] {plan.source_url}")
    archive_data = fetch_bytes(plan.source_url)
    with tarfile.open(fileobj=io.BytesIO(archive_data), mode="r:gz") as tar:
        for asset_file in plan.files:
            member = tar.getmember(asset_file.member)  # type: ignore[arg-type]
            extracted = tar.extractfile(member)
            if extracted is None:
                raise FileNotFoundError(f"Member {asset_file.member} missing from tarball")
            write_file(asset_file.dest, extracted.read())


def compute_hashes(path: Path) -> dict[str, str | int]:
    data = path.read_bytes()
    sha256 = hashlib.sha256(data).hexdigest()
    sha384 = base64.b64encode(hashlib.sha384(data).digest()).decode()
    return {
        "sha256": sha256,
        "sha384": sha384,
        "size": len(data),
    }


def build_manifest(files: Iterable[AssetFile]) -> dict[str, dict[str, str | int]]:
    manifest: dict[str, dict[str, str | int]] = {}
    for asset_file in files:
        rel_path = asset_file.dest.relative_to(VENDOR_DIR)
        metadata = compute_hashes(asset_file.dest)
        metadata["source"] = asset_file.url
        manifest[str(rel_path)] = metadata
    return manifest


def run(force: bool) -> None:
    VENDOR_DIR.mkdir(parents=True, exist_ok=True)

    processed_files: list[AssetFile] = []

    for plan in ASSETS:
        if plan.is_tarball:
            try:
                download_tarball(plan, force=force)
            except (URLError, HTTPError) as exc:
                print(f"[error] Failed to download tarball {plan.source_url}: {exc}", file=sys.stderr)
                raise
        else:
            for asset_file in plan.files:
                try:
                    download_file(plan, asset_file, force=force)
                except (URLError, HTTPError) as exc:
                    print(f"[error] Failed to download {asset_file.url}: {exc}", file=sys.stderr)
                    raise
        processed_files.extend(plan.files)

    manifest = build_manifest(processed_files)
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"[done] Wrote manifest with {len(manifest)} entries to {MANIFEST_PATH}")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download vendored frontend assets")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Redownload assets even if they already exist",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    args = parse_args(sys.argv[1:])
    run(force=args.force)
