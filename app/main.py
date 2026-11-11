"""Точка входу FastAPI. Запуск: uvicorn app.main:create_app --factory --reload"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import router
from app.db import Base, database_url, make_engine, make_session_factory
from app.seed import seed_addresses, seed_schedule


def create_app(db_url: str | None = None, demo_schedule: bool = True) -> FastAPI:
    engine = make_engine(db_url or database_url())
    Base.metadata.create_all(engine)
    session_factory = make_session_factory(engine)
    with session_factory() as session:
        seed_addresses(session)
        if demo_schedule:
            seed_schedule(session)

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        yield
        engine.dispose()  # закриває пул з’єднань при зупинці застосунку

    app = FastAPI(title="СвітлоЛьвів Lite", lifespan=lifespan)
    app.state.engine = engine
    app.state.session_factory = session_factory
    app.include_router(router)
    return app
