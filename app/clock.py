"""Єдине джерело поточного часу.

Графіки відключень і репорти зберігаються в київському часі без tzinfo, тому «зараз»
завжди обчислюється в Europe/Kyiv незалежно від часового поясу сервера (у Docker/CI це UTC).
"""

from datetime import UTC, datetime
from zoneinfo import ZoneInfo

KYIV = ZoneInfo("Europe/Kyiv")


def to_local(moment: datetime) -> datetime:
    """Aware-час переводиться в київський; naive вважається вже київським."""
    if moment.tzinfo is None:
        return moment
    return moment.astimezone(KYIV).replace(tzinfo=None)


def now_local(utc_now: datetime | None = None) -> datetime:
    return to_local(utc_now or datetime.now(UTC))
