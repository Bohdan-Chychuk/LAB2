"""Спільні доменні типи та нормалізація адрес."""

import re
from enum import StrEnum

_STREET_PREFIX = re.compile(r"^(вул\.|вулиця|просп\.|проспект|пл\.|площа)\s*", re.IGNORECASE)


def normalize(value: str) -> str:
    return " ".join(value.split()).casefold()


def normalize_street(street: str) -> str:
    return _STREET_PREFIX.sub("", normalize(street))


class PowerState(StrEnum):
    """Стан світла: плановий (за графіком) або фактичний (за репортами)."""

    ON = "on"
    OFF = "off"

    @classmethod
    def from_power(cls, is_on: bool) -> "PowerState":
        return cls.ON if is_on else cls.OFF
