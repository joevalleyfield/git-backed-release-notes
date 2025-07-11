"""Behave environment setup for end-to-end tests.

This module sets up a temporary Git repository and .xlsx input file,
launches the Tornado app server before all tests, and tears everything down after.
"""

from pathlib import Path
import socket
import subprocess
import tempfile
import time
from types import SimpleNamespace


import pandas as pd


def init_repo(repo_path: Path) -> None:
    """Initialize a new Git repository at the given path."""

    subprocess.run(["git", "init"], cwd=repo_path, check=True)
    subprocess.run(
        ["git", "config", "user.name", "Test User"], cwd=repo_path, check=True
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"], cwd=repo_path, check=True
    )


def create_commit(repo_path: Path, message: str) -> str:
    """
    Create a new commit in the repository with the given commit message.

    Returns:
        str: The SHA of the created commit.
    """

    with open(repo_path / "file.txt", "a", encoding="utf-8") as f:
        f.write(f"{message}\n")
    subprocess.run(["git", "add", "."], cwd=repo_path, check=True)
    subprocess.run(["git", "commit", "-m", message], cwd=repo_path, check=True)
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


def tag_commit(repo_path: Path, sha: str, tag_name: str) -> None:
    """
    Create a lightweight tag pointing to the specified commit.

    Args:
        sha (str): The SHA of the commit to tag.
        tag (str): The name of the tag to create.
    """

    subprocess.run(["git", "tag", tag_name, sha], cwd=repo_path, check=True)


def create_xlsx_file(data_dir: Path) -> Path:
    """
    Create a minimal Excel (.xlsx) file with one row of commit metadata.

    Args:
        data_dir (Path): Full to create the file in.

    Returns:
        Path: The path to the created file.
    """
    data_dir.mkdir(parents=True, exist_ok=True)
    xlsx_path = data_dir / "test_data.xlsx"

    df = pd.DataFrame(
        [
            {
                "id": "c1",
                "sha": "dummysha",
                "labels": "",
                "issue": "",
                "release": "",
                "author_date": "",
                "message": "Initial commit",
                "previous refs": "",
                "initial release": "",
            }
        ]
    )
    df.to_excel(xlsx_path, index=False)
    return xlsx_path


def is_port_open(host, port):
    """Return True if the given host:port is accepting TCP connections."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        return sock.connect_ex((host, port)) == 0


def launch_server(xlsx_path: Path, repo_path: Path, port: int = 8888) -> subprocess.Popen:
    """
    Start the app server as a subprocess and wait for it to become available.

    Returns:
        subprocess.Popen: The running server process.
    """
    proc = subprocess.Popen(
        ["python", "app.py", str(xlsx_path), "--repo", str(repo_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    for _ in range(50):
        if is_port_open("localhost", port):
            break
        time.sleep(0.1)
    else:
        proc.terminate()
        proc.wait()
        raise RuntimeError("Server did not start in time")

    return proc


def create_fixture_repo(repo_path):
    """
    Initialize fixture repo with three commits and tags.

    Returns:
        SimpleNamespace with:
        - shas: list of commit SHAs [initial, middle, latest]
        - tag_to_sha: dict mapping tag names to SHAs
    """
    init_repo(repo_path)

    sha_a = create_commit(repo_path, "First commit (tagged)")
    tag_commit(repo_path, sha_a, "rel-0.1")

    sha_b = create_commit(repo_path, "Second commit (middle)")

    sha_c = create_commit(repo_path, "Third commit (latest)")
    tag_commit(repo_path, sha_c, "rel-0.2")

    return SimpleNamespace(
        shas=[sha_a, sha_b, sha_c], tag_to_sha={"rel-0.1": sha_a, "rel-0.2": sha_c}
    )


def before_all(context):
    """Set up test data and launch the app server before any tests run.

    Creates:
    - Temporary .xlsx file with minimal commit metadata
    - Temporary Git repository with a single tagged commit
    - Starts app server pointing at both
    """

    # Setup temporary directory
    context.tmp_dir_obj = tempfile.TemporaryDirectory()
    context.tmp_dir = Path(context.tmp_dir_obj.name)

    context.repo_path = context.tmp_dir / "repo"
    context.xlsx_path = create_xlsx_file(context.tmp_dir)

    # Create repo and commit
    context.repo_path.mkdir()
    context.fixture_repo = create_fixture_repo(repo_path=context.repo_path)

    # Create xlsx file
    context.xlsx_path = create_xlsx_file(context.tmp_dir)

    # Start the server
    context.server_proc = launch_server(context.xlsx_path, context.repo_path)
    context.base_url = "http://localhost:8888"


def after_all(context):
    """Clean up the server process and temp directories."""
    if hasattr(context, "server_proc"):
        context.server_proc.terminate()
        context.server_proc.wait()

    if hasattr(context, "tmp_dir_obj"):
        context.tmp_dir_obj.cleanup()
