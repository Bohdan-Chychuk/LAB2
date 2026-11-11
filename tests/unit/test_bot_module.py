"""SVL-42: модуль бота не має побічних ефектів під час імпорту, хендлери працюють через DI."""

import asyncio
import importlib
import sys
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

pytest.importorskip("aiogram")


def run(coro):
    """asyncio.run в окремому потоці: Playwright (e2e) тримає event loop у головному."""
    with ThreadPoolExecutor(1) as pool:
        return pool.submit(asyncio.run, coro).result()


def test_import_does_not_touch_database(tmp_path, monkeypatch):
    db_file = tmp_path / "bot.db"
    monkeypatch.setenv("SVL_DB_URL", f"sqlite:///{db_file.as_posix()}")
    sys.modules.pop("bot.bot", None)
    importlib.import_module("bot.bot")
    assert not db_file.exists()


def test_handlers_use_injected_session_factory(db_url):
    from app.bootstrap import init_database
    from bot.bot import create_dispatcher, get_status, set_address

    engine, session_factory = init_database(db_url)
    dp = create_dispatcher(session_factory)
    deps = {k: dp.workflow_data[k] for k in ("session_factory", "user_addresses")}
    message = SimpleNamespace(from_user=SimpleNamespace(id=42), answer=AsyncMock())

    run(set_address(message, SimpleNamespace(args="Шевченка 10"), **deps))
    run(get_status(message, **deps))
    engine.dispose()

    first, second = (call.args[0] for call in message.answer.await_args_list)
    assert first == "Шевченка, 10 — черга 2"
    assert second.startswith("Шевченка, 10 (черга 2)")
