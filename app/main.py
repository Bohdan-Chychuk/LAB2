"""Точка входу FastAPI. Запуск: uvicorn app.main:create_app --factory --reload"""

from fastapi import FastAPI

from app.api.routes import router
from app.db import Base, database_url, make_engine, make_session_factory
from app.seed import seed_addresses


def create_app(db_url: str | None = None) -> FastAPI:
    engine = make_engine(db_url or database_url())
    Base.metadata.create_all(engine)
    session_factory = make_session_factory(engine)
    with session_factory() as session:
        seed_addresses(session)

    app = FastAPI(title="СвітлоЛьвів Lite")
    app.state.session_factory = session_factory
    app.include_router(router)
    return app
