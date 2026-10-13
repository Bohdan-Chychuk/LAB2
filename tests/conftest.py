"""Спільні фікстури: тимчасова SQLite БД, сесія та TestClient."""

import pytest
from fastapi.testclient import TestClient

from app.db import Base, make_engine, make_session_factory
from app.main import create_app


@pytest.fixture
def db_url(tmp_path) -> str:
    return f"sqlite:///{(tmp_path / 'test.db').as_posix()}"


@pytest.fixture
def session(db_url):
    engine = make_engine(db_url)
    Base.metadata.create_all(engine)
    with make_session_factory(engine)() as s:
        yield s
    engine.dispose()


@pytest.fixture
def client(db_url):
    with TestClient(create_app(db_url)) as c:
        yield c
