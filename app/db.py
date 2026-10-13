"""Підключення до БД: engine, фабрика сесій і базовий клас моделей."""

import os

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DEFAULT_DB_URL = "sqlite:///./svitlolviv.db"


class Base(DeclarativeBase):
    pass


def database_url() -> str:
    return os.getenv("SVL_DB_URL", DEFAULT_DB_URL)


def make_engine(url: str) -> Engine:
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, connect_args=connect_args)


def make_session_factory(engine: Engine) -> sessionmaker:
    return sessionmaker(bind=engine, expire_on_commit=False)
