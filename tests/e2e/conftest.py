"""Запуск uvicorn з тимчасовою БД для e2e-тестів Playwright."""

import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import httpx
import pytest

ROOT = Path(__file__).resolve().parents[2]


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@pytest.fixture(scope="session")
def live_server(tmp_path_factory):
    port = _free_port()
    db = tmp_path_factory.mktemp("e2e") / "e2e.db"
    env = {**os.environ, "SVL_DB_URL": f"sqlite:///{db.as_posix()}"}
    cmd = [sys.executable, "-m", "uvicorn", "app.main:create_app", "--factory", "--port", str(port)]
    proc = subprocess.Popen(cmd, cwd=ROOT, env=env)
    url = f"http://127.0.0.1:{port}"
    for _ in range(100):
        try:
            if httpx.get(f"{url}/health").status_code == 200:
                break
        except httpx.HTTPError:
            time.sleep(0.1)
    else:
        proc.terminate()
        pytest.fail("uvicorn не стартував")
    yield url
    proc.terminate()
    proc.wait(timeout=10)
