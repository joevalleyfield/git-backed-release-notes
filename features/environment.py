"""Behave environment setup for end-to-end tests.

This module sets up a temporary Git repository and .xlsx input file,
launches the Tornado app server before all tests, and tears everything down after.
"""

from dataclasses import dataclass
from io import StringIO
from pathlib import Path
import socket
import subprocess
import tempfile
import threading
import time
from types import SimpleNamespace

from behave import fixture, use_fixture

import pandas as pd


# --- DATA STRUCTURES ---


@dataclass
class ServerProcess:
    """Manage a running instance of the Tornado app server for testing.

    Captures subprocess, buffered stdout/stderr, and the base URL of the server.
    Provides a shutdown method and a classmethod launcher. The buffered logs
    can be retrieved after shutdown for debugging test failures.
    """

    proc: subprocess.Popen
    stdout: StringIO
    stderr: StringIO
    base_url: str

    def shutdown(self):
        """Terminate the server process and wait for it to exit."""
        self.proc.terminate()
        self.proc.wait()

    def get_stdout(self) -> str:
        """Return all buffered stdout from the server process."""
        return self.stdout.getvalue()

    def get_stderr(self) -> str:
        """Return all buffered stderr from the server process."""
        return self.stderr.getvalue()

    @classmethod
    def launch(cls, xlsx_path: Path, repo_path: Path, port: int = 8888):
        """Start the app server subprocess and wait for it to become responsive.

        Args:
            xlsx_path: Path to the input spreadsheet file.
            repo_path: Path to the Git repository.
            port: Port to launch the app server on.

        Returns:
            ServerProcess instance containing handles to the process and its logs.
        """
        proc = subprocess.Popen(
            ["python", "app.py", str(xlsx_path), "--repo", str(repo_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,  # line-buffered
        )
        stdout = StringIO()
        stderr = StringIO()

        def reader(stream, buffer):
            for line in stream:
                buffer.write(line)

        threading.Thread(target=reader, args=(proc.stdout, stdout), daemon=True).start()
        threading.Thread(target=reader, args=(proc.stderr, stderr), daemon=True).start()

        for _ in range(50):
            if is_port_open("localhost", port):
                break
            time.sleep(0.1)
        else:
            proc.terminate()
            raise RuntimeError("Server did not start in time")

        return cls(
            proc=proc, stdout=stdout, stderr=stderr, base_url=f"http://localhost:{port}"
        )


class ServerFarm:
    """Manages one or more lazily-started ServerProcess instances by mode."""

    def __init__(self, repo_path: Path, xlsx_path: Path, starting_port: int = 8888):
        self.repo_path = repo_path
        self.xlsx_path = xlsx_path
        self.port_counter = starting_port
        self.servers: dict[str, ServerProcess] = {}

    def get(self, mode: str) -> ServerProcess:
        """Get or launch a server for the given mode."""
        if mode not in self.servers:
            port = self._next_port()
            use_xlsx = (mode == "xlsx")
            server = ServerProcess.launch(
                self.xlsx_path if use_xlsx else None,
                self.repo_path,
                port=port,
            )
            self.servers[mode] = server
        return self.servers[mode]

    def shutdown_all(self):
        """Shut down all running servers."""
        for server in self.servers.values():
            server.shutdown()

    def _next_port(self) -> int:
        port = self.port_counter
        self.port_counter += 1
        return port


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
def server_farm(context, **_kwargs):
    """Create a ServerFarm that manages per-mode app servers."""
    farm = ServerFarm(context.repo_path, context.xlsx_path)
    context.server_farm = farm
    yield farm
    farm.shutdown_all()


@fixture
def composite_fixture(context, **_kwargs):
    """Run all core setup fixtures: temp directory, Git repo, xlsx file, and app server."""

    use_fixture(temp_directory, context)
    use_fixture(git_repo, context)
    use_fixture(xlsx_file, context)
    use_fixture(server_farm, context)


# --- BEHAVE HOOKS ---


def before_all(context):
    """Apply the composite fixture at the start of the test suite."""

    use_fixture(composite_fixture, context)


def before_scenario(context, scenario):
    mode = "xlsx" if "with_xlsx" in scenario.effective_tags else "no_xlsx"
    context.server = context.server_farm.get(mode)


def after_scenario(context, scenario):
    """Attach server logs to the scenario and print them if the scenario failed."""
    if hasattr(context, "server"):
        scenario.stdout = context.server.get_stdout()
        scenario.stderr = context.server.get_stderr()

        if scenario.status == "failed":
            print("\n--- Server STDOUT ---\n", scenario.stdout)
            print("\n--- Server STDERR ---\n", scenario.stderr)


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
