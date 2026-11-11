"""Ініціалізація БД, спільна для веб-застосунку і Telegram-бота."""

from sqlalchemy import Engine
from sqlalchemy.orm import sessionmaker

from app.db import Base, database_url, make_engine, make_session_factory
from app.seed import seed_addresses, seed_schedule


def init_database(
    url: str | None = None, *, demo_schedule: bool = True
) -> tuple[Engine, sessionmaker]:
    """Створює таблиці й наповнює демо-даними. Викликач відповідає за engine.dispose()."""
    engine = make_engine(url or database_url())
    Base.metadata.create_all(engine)
    session_factory = make_session_factory(engine)
    with session_factory() as session:
        seed_addresses(session)
        if demo_schedule:
            seed_schedule(session)
    return engine, session_factory
