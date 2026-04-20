from __future__ import annotations

from util.config import APPLIANCE_LIBRARY


class ApplianceCatalog:
    """Provides appliance/room lookups from the configured appliance library."""

    def __init__(self, appliance_library: dict[str, dict[str, int]] | None = None) -> None:
        self._library = appliance_library or APPLIANCE_LIBRARY

    def rooms(self) -> list[str]:
        return list(self._library.keys())

    def appliances_for_room(self, room: str) -> list[str]:
        return list(self._library.get(room, {}).keys())

    def wattage_for(self, room: str, appliance: str) -> int:
        if room not in self._library or appliance not in self._library[room]:
            raise KeyError(f"Unknown room/appliance pair: {room} / {appliance}")
        return self._library[room][appliance]
