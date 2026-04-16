"""
Computation engine for WattzUp.

This module contains cost calculations, record construction, summaries,
rankings, and budget checks.
"""

from __future__ import annotations


def compute_cost(wattage: int, hours_per_day: int, rate: float = 12.0) -> dict:
    """
    Compute monthly energy use and monthly cost.

    Formula:
    - kWh = (wattage * hours_per_day * 30) / 1000
    - monthly_cost = kWh * rate
    """
    kwh = (wattage * hours_per_day * 30) / 1000
    monthly_cost = kwh * rate

    return {
        "kwh": round(kwh, 2),
        "monthly_cost": round(monthly_cost, 2),
    }


def build_record(
    room: str,
    appliance: str,
    wattage: int,
    usage_level: str,
    hours_per_day: int,
    rate: float = 12.0,
) -> dict:
    """Build one appliance record using the shared data contract."""
    cost_info = compute_cost(wattage, hours_per_day, rate)

    return {
        "room": room,
        "appliance": appliance,
        "wattage": wattage,
        "usage_level": usage_level,
        "hours_per_day": hours_per_day,
        "kwh": cost_info["kwh"],
        "monthly_cost": cost_info["monthly_cost"],
    }


def get_total_cost(records: list[dict]) -> float:
    """Return total monthly cost from all records."""
    total = sum(record.get("monthly_cost", 0.0) for record in records)
    return round(total, 2)


def rank_by_room(records: list[dict]) -> list[tuple[str, float]]:
    """
    Group records by room and return sorted (room, total_cost) pairs.

    Sorting: highest total cost first.
    """
    room_totals: dict[str, float] = {}

    for record in records:
        room = record.get("room")
        monthly_cost = float(record.get("monthly_cost", 0.0))
        if room is None:
            continue
        room_totals[room] = room_totals.get(room, 0.0) + monthly_cost

    ranked = sorted(room_totals.items(), key=lambda item: item[1], reverse=True)
    return [(room, round(total, 2)) for room, total in ranked]


def rank_by_appliance(records: list[dict]) -> list[dict]:
    """Return records sorted by monthly_cost descending."""
    return sorted(records, key=lambda record: record.get("monthly_cost", 0.0), reverse=True)


def check_budget(total_cost: float, budget: float | None) -> str:
    """Return budget status string based on total cost and user budget."""
    if budget is None:
        return "No budget set"
    if total_cost <= budget:
        return "UNDER BUDGET"
    return "OVER BUDGET"


STUB_RECORDS = [
    {
        "room": "Kitchen",
        "appliance": "Rice Cooker",
        "wattage": 400,
        "usage_level": "Moderate",
        "hours_per_day": 4,
        "kwh": 48.0,
        "monthly_cost": 576.0,
    },
    {
        "room": "Living Room",
        "appliance": "Aircon",
        "wattage": 1500,
        "usage_level": "Heavy",
        "hours_per_day": 8,
        "kwh": 360.0,
        "monthly_cost": 4320.0,
    },
]
