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

from behave import fixture, use_fixture

import pandas as pd


# --- FIXTURES ---


@fixture
def temp_directory(context, **_kwargs):
    """Create and register a temporary directory on the context."""

    context.tmp_dir_obj = tempfile.TemporaryDirectory()
    context.tmp_dir = Path(context.tmp_dir_obj.name)
    yield context.tmp_dir
    context.tmp_dir_obj.cleanup()


@fixture
def git_repo(context, **_kwargs):
    """Initialize a Git repo with three commits and two tags."""

    repo_path = context.tmp_dir / "repo"
    repo_path.mkdir()
    init_repo(repo_path)

    sha_a = create_commit(repo_path, "First commit (tagged)")
    tag_commit(repo_path, sha_a, "rel-0.1")
    sha_b = create_commit(repo_path, "Second commit (middle)")
    sha_c = create_commit(repo_path, "Third commit (latest)")
    tag_commit(repo_path, sha_c, "rel-0.2")

    context.repo_path = repo_path
    context.fixture_repo = SimpleNamespace(
        shas=[sha_a, sha_b, sha_c], tag_to_sha={"rel-0.1": sha_a, "rel-0.2": sha_c}
    )
    yield repo_path


@fixture
def xlsx_file(context, **_kwargs):
    """Create and register a minimal .xlsx file on the context."""

    path = create_xlsx_file(context.tmp_dir)
    context.xlsx_path = path
    yield path


@fixture
def app_server(context, **_kwargs):
    """Launch the app server and tear it down after use."""

    proc = launch_server(context.xlsx_path, context.repo_path)
    context.server_proc = proc
    context.base_url = "http://localhost:8888"
    yield proc
    proc.terminate()
    proc.wait()


@fixture
def composite_fixture(context, **_kwargs):
    """Run all core setup fixtures: temp directory, Git repo, xlsx file, and app server."""

    use_fixture(temp_directory, context)
    use_fixture(git_repo, context)
    use_fixture(xlsx_file, context)
    use_fixture(app_server, context)


# --- BEHAVE HOOKS ---


def before_all(context):
    """Apply the composite fixture at the start of the test suite."""

    use_fixture(composite_fixture, context)


# --- UTILITY FUNCTIONS ---


def init_repo(repo_path: Path) -> None:
    """Initialize a Git repository with user config."""

    subprocess.run(["git", "init"], cwd=repo_path, check=True)
    subprocess.run(
        ["git", "config", "user.name", "Test User"], cwd=repo_path, check=True
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"], cwd=repo_path, check=True
    )


def create_commit(repo_path: Path, message: str) -> str:
    """Create a commit with the given message and return its SHA."""

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
    """Create a lightweight tag pointing to the specified commit SHA."""

    subprocess.run(["git", "tag", tag_name, sha], cwd=repo_path, check=True)


def create_xlsx_file(data_dir: Path) -> Path:
    """Generate a minimal Excel file with dummy commit metadata."""

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
    """Check whether the specified host:port is accepting TCP connections."""

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        return sock.connect_ex((host, port)) == 0


def launch_server(
    xlsx_path: Path, repo_path: Path, port: int = 8888
) -> subprocess.Popen:
    """Start the app server subprocess and wait until it is accepting connections."""

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
