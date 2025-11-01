"""Behave environment setup for end-to-end tests.

This module sets up a temporary Git repository and .xlsx input file,
launches the Tornado app server before all tests, and tears everything down after.
"""

import os
import subprocess
import sys
import tempfile
import threading
import time
from dataclasses import dataclass
from io import StringIO
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
from behave import fixture, use_fixture
from features.support.git_helpers import create_commit, init_repo, tag_commit
from features.support.issue_helpers import link_commit_to_issue
from playwright.sync_api import sync_playwright

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
if SRC_DIR.exists() and str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

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
    mode: str = "Unknown"

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

        argv = [sys.executable, "-m", "git_release_notes"]

        if xlsx_path is not None:
            argv += ["--excel-path", str(xlsx_path)]

        argv += ["--repo", str(repo_path), "--port", str(port)]
        argv += ["--no-browser"]
        argv += ["--debug"]

        env = os.environ.copy()
        src_dir = ROOT_DIR / "src"
        existing_pythonpath = env.get("PYTHONPATH", "")
        path_parts = [str(src_dir)]
        if existing_pythonpath:
            path_parts.append(existing_pythonpath)
        env["PYTHONPATH"] = os.pathsep.join(path_parts)

        proc = subprocess.Popen(
            argv,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,  # line-buffered
            env=env,
        )
        stdout = StringIO()
        stderr = StringIO()

        def reader(stream, buffer):
            for line in stream:
                buffer.write(line)

        threading.Thread(target=reader, args=(proc.stdout, stdout), daemon=True).start()
        threading.Thread(target=reader, args=(proc.stderr, stderr), daemon=True).start()

        try:
            wait_for_server_ready(proc, stdout, stderr)
        except Exception:
            proc.terminate()
            try:
                proc.wait(timeout=1)
            except subprocess.TimeoutExpired:
                proc.kill()
            raise

        return cls(proc=proc, stdout=stdout, stderr=stderr, base_url=f"http://localhost:{port}")


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
            attempts = 0
            while True:
                attempts += 1
                port = self._next_port()
                use_xlsx = mode == "xlsx"
                try:
                    server = ServerProcess.launch(
                        self.xlsx_path if use_xlsx else None,
                        self.repo_path,
                        port=port,
                    )
                    server.mode = mode
                    self.servers[mode] = server
                    break
                except RuntimeError as exc:
                    if "Address already in use" in str(exc) and attempts < 5:
                        continue
                    raise
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

    sha_example = create_commit(repo_path, "Example commit for issue view")
    link_commit_to_issue(repo_path, sha_example, "foo-bar")

    context.repo_path = repo_path
    context.fixture_repo = SimpleNamespace(
        shas=[sha_a, sha_b, sha_c, sha_example],
        tag_to_sha={"rel-0.1": sha_a, "rel-0.2": sha_c},
        sha_map={
            "initial": sha_a,
            "middle": sha_b,
            "latest": sha_c,
            "example": sha_example,
        },
        issue_map={
            # semantic mapping of commits to seeded issue slugs
            "allow-editing": sha_a,
            "display-issue-slugs-in-index": sha_b,
        },
    )

    yield repo_path


@fixture
def xlsx_file(context, **_kwargs):
    """Create and register a minimal .xlsx file on the context."""

    path = create_xlsx_file(context.tmp_dir, context.fixture_repo)
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


@fixture
def playwright_browser(context, *args, **kwargs):
    context.playwright = sync_playwright().start()
    context.browser = context.playwright.chromium.launch(headless=True)
    context.page = context.browser.new_page()
    yield context.page
    context.browser.close()
    context.playwright.stop()


# --- BEHAVE HOOKS ---


def before_all(context):
    """Apply the composite fixture at the start of the test suite."""

    use_fixture(composite_fixture, context)


def before_tag(context, tag):
    if tag == "javascript":
        use_fixture(playwright_browser, context)


def before_scenario(context, scenario):
    """Behave hook: Selects and launches the appropriate server fixture for the test.

    Chooses between server modes (e.g. with or without .xlsx file) based on scenario tags.
    The server is launched lazily via context.server_farm.get(mode).
    """
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


def create_xlsx_file(data_dir: Path, fixture_repo: SimpleNamespace) -> Path:
    """Generate a minimal Excel file with dummy commit metadata."""

    data_dir.mkdir(parents=True, exist_ok=True)
    xlsx_path = data_dir / "test_data.xlsx"
    df = pd.DataFrame(
        [
            {
                "id": "c1",
                "sha": fixture_repo.shas[0],
                "issue": "allow-editing",
                "release": "",
                "author_date": "",
                "message": "Initial commit",
                "previous refs": "",
                "initial release": "",
            },
            {
                "id": "c2",
                "sha": fixture_repo.shas[1],
                "issue": "display-issue-slugs-in-index",  # used by edit_commit.feature
                "release": "",
                "author_date": "",
                "message": "Second commit",
            },
        ]
    )
    df.to_excel(xlsx_path, index=False)
    return xlsx_path


def wait_for_server_ready(proc, stdout_buf, stderr_buf, max_attempts=50, interval=0.1):
    """Waits for the server process to print its readiness signal to stdout.

    Monitors the process's stdout buffer for a known readiness message.
    Fails early if the process exits or if the timeout (max_attempts × interval) is exceeded.

    Args:
        proc: The subprocess.Popen object for the server.
        stdout_buf: A StringIO capturing the server's stdout.
        stderr_buf: A StringIO capturing the server's stderr.
        max_attempts: Maximum number of polling attempts (default: 50).
        interval: Time in seconds between polling attempts (default: 0.1).

    Raises:
        RuntimeError: If the server exits prematurely or fails to signal readiness.
    """
    for _ in range(max_attempts):
        time.sleep(interval)
        if "Server running at http://localhost" in stdout_buf.getvalue():
            return
        if proc.poll() is not None:
            raise RuntimeError(
                f"Server exited early with code {proc.returncode}\n"
                f"STDOUT:\n{stdout_buf.getvalue()[-1000:]}\n"
                f"STDERR:\n{stderr_buf.getvalue()[-1000:]}"
            )
    raise RuntimeError("Server did not signal readiness in time")
