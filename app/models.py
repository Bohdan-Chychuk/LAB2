"""ORM-моделі: адреси, графіки черг, підписки на сповіщення, репорти."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Address(Base):
    __tablename__ = "addresses"

    id: Mapped[int] = mapped_column(primary_key=True)
    street: Mapped[str] = mapped_column(String(100), index=True)
    house: Mapped[str] = mapped_column(String(20))
    queue: Mapped[int] = mapped_column(Integer)


class Schedule(Base):
    """Актуальний графік черги у канонічному вигляді "08:00-12:00, 16:00-20:00"."""

    __tablename__ = "schedules"

    queue: Mapped[int] = mapped_column(Integer, primary_key=True)
    intervals: Mapped[str] = mapped_column(String(500))
    version: Mapped[int] = mapped_column(Integer, default=1)


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(String(64), index=True)
    street: Mapped[str] = mapped_column(String(100))
    house: Mapped[str] = mapped_column(String(20))
    queue: Mapped[int] = mapped_column(Integer)
    notify_before: Mapped[int] = mapped_column(Integer, default=30)
    quiet_hours: Mapped[bool] = mapped_column(Boolean, default=False)


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(String(64), index=True)
    street: Mapped[str] = mapped_column(String(100), index=True)
    house: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(3))
    created_at: Mapped[datetime] = mapped_column(DateTime, index=True)
