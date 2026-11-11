"""Pydantic-схеми запитів і відповідей REST API (валідація + документація OpenAPI)."""

import datetime as dt

from pydantic import BaseModel, Field, PositiveInt, field_validator

from app.services.parser import parse_intervals


class ScheduleIn(BaseModel):
    """Графік відключень від оператора: {"queues": {"1": "08:00-12:00, 16:00-20:00"}}."""

    date: dt.date | None = None
    source: str | None = None
    queues: dict[PositiveInt, str] = Field(min_length=1)

    @field_validator("queues")
    @classmethod
    def intervals_must_parse(cls, queues: dict[int, str]) -> dict[int, str]:
        for text in queues.values():
            parse_intervals(text)  # ScheduleParseError — підклас ValueError -> 422
        return queues
