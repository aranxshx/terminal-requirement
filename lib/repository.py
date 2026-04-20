from __future__ import annotations

import csv
import os
import re

from lib.models import ApplianceRecord
from util.config import DATA_DIRECTORY, USER_RECORD_SUFFIX


class HouseholdRecordRepository:
    """Persists and retrieves per-user household appliance usage records."""

    _FIELDNAMES = [
        "room",
        "appliance",
        "wattage",
        "usage_level",
        "hours_per_day",
        "kwh",
        "monthly_cost",
    ]

    def __init__(self, data_directory: str = DATA_DIRECTORY, file_suffix: str = USER_RECORD_SUFFIX) -> None:
        self.data_directory = data_directory
        self.file_suffix = file_suffix
        os.makedirs(self.data_directory, exist_ok=True)

    @staticmethod
    def sanitize_username(username: str) -> str:
        safe = re.sub(r"[^A-Za-z0-9_-]+", "_", username.strip())
        return safe.strip("_-")

    def user_file_path(self, username: str) -> str:
        return os.path.join(self.data_directory, f"{username}{self.file_suffix}")

    def list_usernames(self) -> list[str]:
        if not os.path.isdir(self.data_directory):
            return []

        found: dict[str, str] = {}
        for entry in sorted(os.listdir(self.data_directory), key=str.lower):
            if not entry.endswith(self.file_suffix):
                continue
            username = entry[: -len(self.file_suffix)]
            if username:
                found.setdefault(username.lower(), username)

        return list(found.values())

    def username_exists(self, username: str) -> bool:
        normalized = username.lower()
        return any(existing.lower() == normalized for existing in self.list_usernames())

    def save_for_user(self, username: str, records: list[ApplianceRecord]) -> None:
        filepath = self.user_file_path(username)
        with open(filepath, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=self._FIELDNAMES)
            writer.writeheader()
            for record in records:
                writer.writerow(record.to_dict())

    def load_for_user(self, username: str) -> list[ApplianceRecord]:
        filepath = self.user_file_path(username)
        if not os.path.exists(filepath):
            return []

        records: list[ApplianceRecord] = []
        with open(filepath, "r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                record = self._row_to_record(row)
                if record is not None:
                    records.append(record)

        return records

    def _row_to_record(self, row: dict[str, str]) -> ApplianceRecord | None:
        try:
            room = str(row["room"]).strip()
            appliance = str(row["appliance"]).strip()
            usage_level = str(row["usage_level"]).strip()
            if not room or not appliance or not usage_level:
                return None

            record = ApplianceRecord(
                room=room,
                appliance=appliance,
                wattage=int(row["wattage"]),
                usage_level=usage_level,
                hours_per_day=int(row["hours_per_day"]),
                kwh=float(row["kwh"]),
                monthly_cost=float(row["monthly_cost"]),
            )
        except (KeyError, TypeError, ValueError):
            return None

        if record.wattage < 0 or record.hours_per_day < 0 or record.kwh < 0 or record.monthly_cost < 0:
            return None

        return record
