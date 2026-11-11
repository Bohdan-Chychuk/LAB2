"""Спільні доменні типи."""

from enum import StrEnum


class PowerState(StrEnum):
    """Стан світла: плановий (за графіком) або фактичний (за репортами)."""

    ON = "on"
    OFF = "off"

    @classmethod
    def from_power(cls, is_on: bool) -> "PowerState":
        return cls.ON if is_on else cls.OFF
