"""
feature.py

This file contains `common` structs and classes that are used in multiple places.
"""

from typing import Optional

import pydantic


class DamageSchedule(pydantic.BaseModel):
    """
    Jointly contains damage and hit.
    """

    damage: float
    hit: float
    time: float


class PeriodicFeature(pydantic.BaseModel):
    """
    Jointly contains damage and hit, interval.
    This contains information about periodic system.
    """

    damage: float
    hit: float
    interval: float
    initial_delay: Optional[float] = pydantic.Field(default=None)
