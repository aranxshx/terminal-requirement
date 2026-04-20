from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass(slots=True)
class ApplianceRecord:
    """Represents one appliance usage entry for monthly electricity tracking."""

    room: str
    appliance: str
    wattage: int
    usage_level: str
    hours_per_day: int
    kwh: float
    monthly_cost: float

    def to_dict(self) -> dict[str, Any]:
        """Return record data in dictionary form for UI and persistence compatibility."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ApplianceRecord":
        """Create an ApplianceRecord from untyped dictionary data."""
        return cls(
            room=str(data["room"]),
            appliance=str(data["appliance"]),
            wattage=int(data["wattage"]),
            usage_level=str(data["usage_level"]),
            hours_per_day=int(data["hours_per_day"]),
            kwh=float(data["kwh"]),
            monthly_cost=float(data["monthly_cost"]),
        )
