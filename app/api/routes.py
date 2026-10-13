"""REST-ендпоінти. Тонкий шар над app/services."""

from collections.abc import Iterator

from fastapi import APIRouter, Request
from sqlalchemy.orm import Session

router = APIRouter()


def get_session(request: Request) -> Iterator[Session]:
    with request.app.state.session_factory() as session:
        yield session


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}
