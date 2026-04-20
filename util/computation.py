"""Computation adapters for backward compatibility.

This module keeps the original function names while delegating behavior to
object-oriented services.
"""

from __future__ import annotations

from lib.models import ApplianceRecord
from lib.services import BudgetService, EnergyComputationService, RankingService


class ComputationFacade:
    """Facade over computation and reporting services."""

    def __init__(self) -> None:
        self._energy = EnergyComputationService()
        self._ranking = RankingService()
        self._budget = BudgetService()

    def compute_cost(self, wattage: int, hours_per_day: int) -> dict[str, float]:
        scaled_kwh = round((wattage * hours_per_day * 30) / 1000, 2)
        scaled_cost = round(scaled_kwh * self._energy.rate_per_kwh, 2)
        return {"kwh": scaled_kwh, "monthly_cost": scaled_cost}

    def build_record(
        self,
        room: str,
        appliance: str,
        wattage: int,
        usage_level: str,
        hours_per_day: int | None = None,
    ) -> dict:
        del hours_per_day
        return self._energy.build_record(room, appliance, wattage, usage_level).to_dict()

    def get_total_cost(self, records: list[dict]) -> float:
        record_objs = [ApplianceRecord.from_dict(record) for record in records]
        return self._energy.total_cost(record_objs)

    def rank_by_room(self, records: list[dict]) -> list[tuple[str, float]]:
        record_objs = [ApplianceRecord.from_dict(record) for record in records]
        return self._ranking.rank_rooms(record_objs)

    def rank_by_appliance(self, records: list[dict]) -> list[dict]:
        record_objs = [ApplianceRecord.from_dict(record) for record in records]
        return [record.to_dict() for record in self._ranking.rank_appliances(record_objs)]

    def check_budget(self, total_cost: float, budget: float | None) -> str:
        status = self._budget.budget_status(total_cost, budget)
        if status == "NOT SET":
            return "No budget set"
        return status


_FACADE = ComputationFacade()


# Backward-compatible function exports.
def compute_cost(wattage: int, hours_per_day: int, rate: float = 12.0) -> dict:
    del rate
    return _FACADE.compute_cost(wattage, hours_per_day)


def build_record(
    room: str,
    appliance: str,
    wattage: int,
    usage_level: str,
    hours_per_day: int,
    rate: float = 12.0,
) -> dict:
    del rate
    return _FACADE.build_record(room, appliance, wattage, usage_level, hours_per_day)


def get_total_cost(records: list[dict]) -> float:
    return _FACADE.get_total_cost(records)


def rank_by_room(records: list[dict]) -> list[tuple[str, float]]:
    return _FACADE.rank_by_room(records)


def rank_by_appliance(records: list[dict]) -> list[dict]:
    return _FACADE.rank_by_appliance(records)


def check_budget(total_cost: float, budget: float | None) -> str:
    return _FACADE.check_budget(total_cost, budget)
