"""Behave environment setup for end-to-end tests.

This module sets up a temporary Git repository and .xlsx input file,
launches the Tornado app server before all tests, and tears everything down after.
"""

import os
import socket
import subprocess
import tempfile
import time

import pandas as pd


def is_port_open(host, port):
    """Return True if the given host:port is accepting TCP connections."""
    with socket.socket() as sock:
        return sock.connect_ex((host, port)) == 0


def before_all(context):
    """Set up test data and launch the app server before any tests run.

    Creates:
    - Temporary .xlsx file with minimal commit metadata
    - Temporary Git repository with a single tagged commit
    - Starts app server pointing at both
    """
    # Step 1: Create .xlsx file
    context.data_dir = tempfile.TemporaryDirectory()
    xlsx_path = os.path.join(context.data_dir.name, "test_data.xlsx")

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
    context.xlsx_path = xlsx_path

    # Step 2: Create fixture git repo
    context.repo_dir = tempfile.TemporaryDirectory()
    repo_path = context.repo_dir.name

    subprocess.run(["git", "init"], cwd=repo_path, check=True)
    with open(os.path.join(repo_path, "README.md"), "w", encoding="utf-8") as f:
        f.write("# Test Repo\n")

    subprocess.run(["git", "add", "README.md"], cwd=repo_path, check=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo_path, check=True)
    subprocess.run(["git", "tag", "rel-0-1"], cwd=repo_path, check=True)

    context.fixture_repo = repo_path

    # Step 3: Start the app server
    context.server_proc = subprocess.Popen(
        ["python", "app.py", xlsx_path, "--repo", repo_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    for _ in range(50):
        if is_port_open("localhost", 8888):
            break
        time.sleep(0.1)
    else:
        raise RuntimeError("Server did not start in time")

    context.base_url = "http://localhost:8888"


def after_all(context):
    """Shut down the app server and clean up temporary files."""
    context.server_proc.terminate()
    context.server_proc.wait()
    context.repo_dir.cleanup()
    context.data_dir.cleanup()
