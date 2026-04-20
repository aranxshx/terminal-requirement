"""Data layer adapters for backward compatibility.

This module preserves the original function-style API while internally using
object-oriented catalog and repository services.
"""

from __future__ import annotations

from lib.catalog import ApplianceCatalog
from lib.models import ApplianceRecord
from lib.repository import HouseholdRecordRepository
from util.config import APPLIANCE_LIBRARY as APPLIANCE_LIBRARY_DATA
from util.config import USAGE_LEVELS as USAGE_LEVELS_DATA


class DataLayerFacade:
    """Facade for room/appliance catalog lookups and record persistence."""

    def __init__(self) -> None:
        self._catalog = ApplianceCatalog()
        self._repository = HouseholdRecordRepository()

    def get_rooms(self) -> list[str]:
        return self._catalog.rooms()

    def get_appliances(self, room: str) -> list[str]:
        return self._catalog.appliances_for_room(room)

    def get_wattage(self, room: str, appliance: str) -> int:
        return self._catalog.wattage_for(room, appliance)

    def save_records(self, records: list[dict], filename: str) -> None:
        username = self._username_from_filename(filename)
        record_objects = [ApplianceRecord.from_dict(record) for record in records]
        self._repository.save_for_user(username, record_objects)

    def load_records(self, filename: str) -> list[dict]:
        username = self._username_from_filename(filename)
        return [record.to_dict() for record in self._repository.load_for_user(username)]

    @staticmethod
    def _username_from_filename(filename: str) -> str:
        marker = "_household_records.csv"
        name = filename.split("/")[-1].split("\\")[-1]
        if name.endswith(marker):
            return name[: -len(marker)]
        raise ValueError(f"Unsupported records filename: {filename}")


_FACADE = DataLayerFacade()


# Backward-compatible values.
APPLIANCE_LIBRARY = APPLIANCE_LIBRARY_DATA
USAGE_LEVELS = USAGE_LEVELS_DATA


# Backward-compatible functions.
def get_rooms() -> list[str]:
    return _FACADE.get_rooms()


def get_appliances(room: str) -> list[str]:
    return _FACADE.get_appliances(room)


def get_wattage(room: str, appliance: str) -> int:
    return _FACADE.get_wattage(room, appliance)


def save_records(records: list[dict], filename: str = "data/household_records.csv") -> None:
    _FACADE.save_records(records, filename)


def load_records(filename: str = "data/household_records.csv") -> list[dict]:
    try:
        return _FACADE.load_records(filename)
    except ValueError:
        return []
