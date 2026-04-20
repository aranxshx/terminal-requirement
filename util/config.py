from __future__ import annotations

APPLIANCE_LIBRARY: dict[str, dict[str, int]] = {
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

USAGE_LEVELS: dict[str, int] = {
    "Heavy": 8,
    "Moderate": 4,
    "Eco": 1,
}

DEFAULT_RATE_PER_KWH: float = 12.0
DATA_DIRECTORY: str = "data"
USER_RECORD_SUFFIX: str = "_household_records.csv"

# UI design tokens (customtkinter)
BG_BASE: str = "#1a1a2e"
BG_SURFACE: str = "#16213e"
BG_ELEVATED: str = "#0f3460"

ACCENT_PRIMARY: str = "#e94560"
ACCENT_HOVER: str = "#c73652"
ACCENT_MUTED: str = "#533483"

TEXT_PRIMARY: str = "#eaeaea"
TEXT_SECONDARY: str = "#a0a0b0"
TEXT_DISABLED: str = "#555566"

STATUS_UNDER: str = "#4caf82"
STATUS_OVER: str = "#e94560"
STATUS_NOTSET: str = "#a0a0b0"

BORDER_DEFAULT: str = "#2a2a4a"
BORDER_FOCUS: str = "#e94560"
