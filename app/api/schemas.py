"""Pydantic-схеми запитів і відповідей REST API (валідація + документація OpenAPI)."""

import datetime as dt
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, PositiveInt, field_validator

from app.domain import PowerState
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


class ApiModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class AddressIn(BaseModel):
    street: str = Field(examples=["Шевченка"])
    house: str = Field(examples=["10"])


class QueueOut(ApiModel):
    street: str
    house: str
    queue: int


class ChangedQueuesOut(BaseModel):
    changed_queues: list[int]


class IntervalOut(BaseModel):
    start: str = Field(examples=["08:00"])
    end: str = Field(examples=["12:00"])


class ScheduleOut(BaseModel):
    queue: int
    intervals: list[IntervalOut]


class StatusOut(ApiModel):
    street: str
    house: str
    queue: int
    now: dt.datetime
    planned: PowerState
    next_change: dt.datetime | None
    next_outage: dt.datetime | None
    minutes_to_outage: int | None
    actual: PowerState | None = Field(description="Фактичний стан за репортами або null")


class SubscriptionIn(AddressIn):
    user_id: str
    notify_before: Literal[15, 30, 60] = 30
    quiet_hours: bool = False


class SubscriptionOut(ApiModel):
    id: int
    user_id: str
    street: str
    house: str
    queue: int
    notify_before: int
    quiet_hours: bool


class NotificationOut(BaseModel):
    user_id: str
    street: str
    house: str
    queue: int
    notify_before: int
    outage_start: dt.datetime


class ReportIn(AddressIn):
    user_id: str
    status: PowerState


class ReportOut(ApiModel):
    id: int
    user_id: str
    street: str
    house: str
    status: PowerState
    created_at: dt.datetime


class HealthOut(BaseModel):
    status: Literal["ok"] = "ok"
