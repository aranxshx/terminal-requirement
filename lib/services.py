from __future__ import annotations

from lib.models import ApplianceRecord
from util.config import DEFAULT_RATE_PER_KWH, USAGE_LEVELS


class EnergyComputationService:
    """Handles electricity usage and monthly cost computations."""

    def __init__(self, rate_per_kwh: float = DEFAULT_RATE_PER_KWH) -> None:
        self.rate_per_kwh = rate_per_kwh

    def build_record(
        self,
        room: str,
        appliance: str,
        wattage: int,
        usage_level: str,
        custom_hours_per_day: float | None = None,
    ) -> ApplianceRecord:
        if custom_hours_per_day is None:
            if usage_level not in USAGE_LEVELS:
                raise ValueError(f"Unknown usage level: {usage_level}")
            hours_per_day = USAGE_LEVELS[usage_level]
        else:
            if custom_hours_per_day <= 0 or custom_hours_per_day > 24:
                raise ValueError("Custom usage hours must be greater than 0 and at most 24.")
            if not float(custom_hours_per_day).is_integer():
                raise ValueError("Custom usage hours must be a whole number.")
            hours_per_day = int(custom_hours_per_day)
            usage_level = f"Custom ({hours_per_day:g}h/day)"

        kwh = (wattage * hours_per_day * 30) / 1000
        monthly_cost = kwh * self.rate_per_kwh

        return ApplianceRecord(
            room=room,
            appliance=appliance,
            wattage=wattage,
            usage_level=usage_level,
            hours_per_day=int(hours_per_day),
            kwh=round(kwh, 2),
            monthly_cost=round(monthly_cost, 2),
        )

    @staticmethod
    def total_cost(records: list[ApplianceRecord]) -> float:
        return round(sum(record.monthly_cost for record in records), 2)


class RankingService:
    """Provides sorted ranking views for appliance and room cost reports."""

    @staticmethod
    def rank_appliances(records: list[ApplianceRecord]) -> list[ApplianceRecord]:
        return sorted(records, key=lambda item: item.monthly_cost, reverse=True)

    @staticmethod
    def rank_rooms(records: list[ApplianceRecord]) -> list[tuple[str, float]]:
        room_totals: dict[str, float] = {}
        for record in records:
            room_totals[record.room] = room_totals.get(record.room, 0.0) + record.monthly_cost

        ranked = sorted(room_totals.items(), key=lambda item: item[1], reverse=True)
        return [(room, round(total, 2)) for room, total in ranked]


class BudgetService:
    """Encapsulates budget status logic."""

    @staticmethod
    def budget_status(total_cost: float, budget: float | None) -> str:
        if budget is None:
            return "NOT SET"
        if total_cost <= budget:
            return "UNDER BUDGET"
        return "OVER BUDGET"
