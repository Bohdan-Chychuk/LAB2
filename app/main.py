"""Точка входу FastAPI. Запуск: uvicorn app.main:create_app --factory --reload"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import router
from app.bootstrap import init_database


def create_app(db_url: str | None = None, demo_schedule: bool = True) -> FastAPI:
    engine, session_factory = init_database(db_url, demo_schedule=demo_schedule)

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        yield
        engine.dispose()  # закриває пул з’єднань при зупинці застосунку

    app = FastAPI(title="СвітлоЛьвів Lite", lifespan=lifespan)
    app.state.engine = engine
    app.state.session_factory = session_factory
    app.include_router(router)
    return app
