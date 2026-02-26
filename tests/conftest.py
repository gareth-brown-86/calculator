"""Pytest configuration and shared fixtures."""

import subprocess
import sys
from pathlib import Path

import pytest

# Add the project root to sys.path so tests can import the backend package.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture(scope="session")
def streamlit_url():
    """Start a single Streamlit server shared across all browser-based tests."""
    from tests.ui_helpers import get_free_port, start_streamlit_server

    port = get_free_port()
    process = start_streamlit_server(PROJECT_ROOT, port)
    yield f"http://127.0.0.1:{port}"
    process.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
