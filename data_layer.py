"""
Data layer for WattzUp.

Data structures:
- APPLIANCE_LIBRARY: nested dictionary mapping room -> appliance -> wattage.
- USAGE_LEVELS: dictionary mapping usage labels to hours per day.
- Record dictionary format:
  {
      "room": str,
      "appliance": str,
      "wattage": int,
      "usage_level": str,
      "hours_per_day": int,
      "kwh": float,
      "monthly_cost": float,
  }
"""

from __future__ import annotations

import csv
import os
from typing import Optional

APPLIANCE_LIBRARY = {
    "Bathroom": {
        "Lights": 15,
        "Hair Dryer": 1200,
        "Charger": 10,
        "Water Heater": 2000,
    },
    "Kitchen": {
        "Rice Cooker": 400,
        "Electric Kettle": 1500,
        "Electric Stove": 1000,
        "Dishwasher": 1800,
        "Lights": 15,
        "Fan": 60,
        "Water Dispenser": 500,
    },
    "Dining Area": {
        "Fan": 60,
        "Lights": 15,
        "Charger": 10,
        "Aircon": 1500,
    },
    "Living Room": {
        "TV": 150,
        "Aircon": 1500,
        "Fan": 60,
        "Lights": 15,
        "Charger": 10,
    },
    "Bedroom": {
        "Charger": 10,
        "Lights": 15,
        "Aircon": 1500,
        "Fan": 60,
        "Lamp": 40,
    },
}

USAGE_LEVELS = {
    "Heavy": 8,
    "Moderate": 4,
    "Eco": 1,
}


def get_rooms() -> list[str]:
    """Return all available room names."""
    return list(APPLIANCE_LIBRARY.keys())


def get_appliances(room: str) -> list[str]:
    """Return appliance names for a given room, or an empty list if room is unknown."""
    room_data = APPLIANCE_LIBRARY.get(room, {})
    return list(room_data.keys())


def get_wattage(room: str, appliance: str) -> int:
    """Return wattage for a room/appliance pair."""
    return APPLIANCE_LIBRARY[room][appliance]


def _parse_record_line(line: str) -> Optional[dict]:
    """Parse one CSV line into a record dict; return None for invalid/corrupted lines."""
    raw = line.strip()
    if not raw:
        return None

    columns = [value.strip() for value in raw.split(",")]
    if len(columns) != 7:
        return None

    room, appliance, wattage_s, usage_level, hours_s, kwh_s, monthly_cost_s = columns

    # Ignore optional header row if present.
    if room.lower() == "room" and appliance.lower() == "appliance":
        return None

    if not room or not appliance or usage_level not in USAGE_LEVELS:
        return None

    try:
        wattage = int(wattage_s)
        hours_per_day = int(hours_s)
        kwh = float(kwh_s)
        monthly_cost = float(monthly_cost_s)
    except ValueError:
        return None

    if wattage < 0 or hours_per_day < 0 or kwh < 0 or monthly_cost < 0:
        return None

    return {
        "room": room,
        "appliance": appliance,
        "wattage": wattage,
        "usage_level": usage_level,
        "hours_per_day": hours_per_day,
        "kwh": kwh,
        "monthly_cost": monthly_cost,
    }


def save_records(records: list[dict], filename: str = "data/household_records.txt") -> None:
    """Save a list of record dictionaries to a CSV-formatted text file."""
    fieldnames = [
        "room",
        "appliance",
        "wattage",
        "usage_level",
        "hours_per_day",
        "kwh",
        "monthly_cost",
    ]

    folder = os.path.dirname(filename)
    if folder:
        os.makedirs(folder, exist_ok=True)

    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            writer.writerow({key: record.get(key) for key in fieldnames})


def load_records(filename: str = "data/household_records.txt") -> list[dict]:
    """Load record dictionaries from file, skipping invalid lines silently."""
    if not os.path.exists(filename):
        return []

    records = []
    with open(filename, "r", encoding="utf-8") as file:
        for line in file:
            record = _parse_record_line(line)
            if record is not None:
                records.append(record)

    return records
