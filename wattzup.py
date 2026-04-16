"""
WattzUp: Electricity Consumption Monitoring System
Final merged single-file submission.
"""

from __future__ import annotations

import csv
import os
import re
from typing import Optional

# =========================
# Part 1 - Data Layer
# =========================

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
    return list(APPLIANCE_LIBRARY.keys())


def get_appliances(room: str) -> list[str]:
    room_data = APPLIANCE_LIBRARY.get(room, {})
    return list(room_data.keys())


def get_wattage(room: str, appliance: str) -> int:
    return APPLIANCE_LIBRARY[room][appliance]


def _parse_record_line(line: str) -> Optional[dict]:
    raw = line.strip()
    if not raw:
        return None

    columns = [value.strip() for value in raw.split(",")]
    if len(columns) != 7:
        return None

    room, appliance, wattage_s, usage_level, hours_s, kwh_s, monthly_cost_s = columns

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
    if not os.path.exists(filename):
        return []

    records = []
    with open(filename, "r", encoding="utf-8") as file:
        for line in file:
            record = _parse_record_line(line)
            if record is not None:
                records.append(record)

    return records


# =========================
# Part 2 - Computation
# =========================


def compute_cost(wattage: int, hours_per_day: int, rate: float = 12.0) -> dict:
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
    return round(sum(record.get("monthly_cost", 0.0) for record in records), 2)


def rank_by_room(records: list[dict]) -> list[tuple[str, float]]:
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
    return sorted(records, key=lambda record: record.get("monthly_cost", 0.0), reverse=True)


def check_budget(total_cost: float, budget: float | None) -> str:
    if budget is None:
        return "No budget set"
    if total_cost <= budget:
        return "UNDER BUDGET"
    return "OVER BUDGET"


# =========================
# Part 3 - UI
# =========================


def display_dashboard(records: list[dict], budget: float | None) -> None:
    """Shows the main dashboard with large ASCII art and consistent borders."""
    total_cost = get_total_cost(records)

    print("\n" + "============================================================================")
    print(r"                                                                          ")
    print(r"  /$$      /$$  /$$$$$$  /$$$$$$$$ /$$$$$$$$ /$$$$$$$$                    ")
    print(r" | $$  /$ | $$ /$$__  $$|__  $$__/|__  $$__/|_____ $$                     ")
    print(r" | $$ /$$$| $$| $$  \ $$   | $$      | $$        /$$/  /$$   /$$  /$$$$$$ ")
    print(r" | $$/$$ $$ $$| $$$$$$$$   | $$      | $$       /$$/  | $$  | $$ /$$__  $$")
    print(r" | $$$$_  $$$$| $$__  $$   | $$      | $$      /$$/   | $$  | $$| $$  \ $$")
    print(r" | $$$/ \  $$$| $$  | $$   | $$      | $$     /$$/    | $$  | $$| $$  | $$")
    print(r" | $$/   \  $$| $$  | $$   | $$      | $$    /$$$$$$$$|  $$$$$$/| $$$$$$$/")
    print(r" |__/     \__/|__/  |__/   |__/      |__/   |________/ \______/ | $$____/ ")
    print(r"                                                                | $$      ")
    print(r"                                                                | $$      ")
    print(r"                                                                |__/      ")
    
    # Border Middle
    print("============================================================================")
    
    if not records:
        print("  Estimated Monthly Cost : P0.00")
        print("  Budget Status          : NO RECORDS YET")
    else:
        print(f"  Estimated Monthly Cost : P{total_cost:,.2f}")
        if budget is None:
            print("  Budget Status          : NOT SET")
        elif total_cost > budget:
            print("  Budget Status          : OVER BUDGET")
        else:
            print("  Budget Status          : UNDER BUDGET")

    print("\n  [1] Manage Household")
    print("  [2] View Appliance Usage Ranking")
    print("  [3] View Room Usage Ranking")
    print("  [4] Set Monthly Budget")
    print("  [5] Save Records")
    print("  [6] Load Records")
    print("  [0] Exit")
    
    # Border Bottom
    print("============================================================================")

def display_room_menu(rooms: list[str]) -> str | None:
    while True:
        print("\nSELECT ROOM:")
        for i, room in enumerate(rooms, 1):
            print(f"  [{i}] {room}")
        print("  [0] Back")

        choice = input("\nEnter choice: ").strip()
        if choice == "0":
            return None

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(rooms):
                return rooms[idx]
            print("Invalid choice. Please select from the list.")
        except ValueError:
            print("Error: Please enter a valid number.")


def display_appliance_menu(appliances: list[str]) -> str | None:
    while True:
        print("\nSELECT APPLIANCE:")
        for i, appliance in enumerate(appliances, 1):
            print(f"  [{i}] {appliance}")
        print("  [0] Back")

        choice = input("\nEnter choice: ").strip()
        if choice == "0":
            return None

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(appliances):
                return appliances[idx]
            print("Invalid choice. Please select from the list.")
        except ValueError:
            print("Error: Please enter a valid number.")


def display_usage_menu() -> str:
    while True:
        print("\nHOW OFTEN DO YOU USE THIS APPLIANCE?")
        print("  [1] Heavy    - 8+ hours/day")
        print("  [2] Moderate - 2 to 8 hours/day")
        print("  [3] Eco      - Less than 2 hours/day")

        choice = input("\nEnter choice: ").strip()
        mapping = {"1": "Heavy", "2": "Moderate", "3": "Eco"}
        if choice in mapping:
            return mapping[choice]
        print("Invalid choice. Please select 1, 2, or 3.")


def display_room_ranking(ranked_rooms: list[tuple[str, float]]) -> None:
    print("\n" + "-" * 35)
    print(f"{'ROOM USAGE RANKING':^35}")
    print("-" * 35)

    if not ranked_rooms:
        print("No data available.")
    else:
        for i, (room, cost) in enumerate(ranked_rooms, 1):
            print(f"  {i}. {room:<18} P{cost:,.2f}")

    print("-" * 35)
    input("\nPress Enter to return to Dashboard...")


def display_appliance_ranking(ranked_appliances: list[dict]) -> None:
    print("\n" + "-" * 45)
    print(f"{'APPLIANCE USAGE RANKING':^45}")
    print("-" * 45)

    if not ranked_appliances:
        print("No data available.")
    else:
        for i, app in enumerate(ranked_appliances, 1):
            name_str = f"{app.get('appliance', 'Unknown')} ({app.get('room', 'Unknown')})"
            print(f"  {i}. {name_str:<26} P{app.get('monthly_cost', 0.0):,.2f}")

    print("-" * 45)
    input("\nPress Enter to return to Dashboard...")


def prompt_budget() -> float:
    while True:
        try:
            val = input("\nEnter monthly budget in pesos (P): ").replace(",", "").strip()
            budget = float(val)
            if budget < 0:
                print("Budget cannot be negative.")
                continue
            return budget
        except ValueError:
            print("Error: Invalid amount. Please enter numbers only.")


# =========================
# Part 4 - Main Loop
# =========================


def clear_records(records: list[dict]) -> list[dict]:
    while True:
        choice = input("Are you sure you want to clear all records? (y/n): ").strip().lower()
        if choice in {"y", "yes"}:
            print("All records have been cleared.")
            return []
        if choice in {"n", "no"}:
            print("Clear canceled.")
            return records
        print("Invalid input. Enter y or n.")


def _prompt_main_menu_choice() -> str:
    valid_choices = {"0", "1", "2", "3", "4", "5", "6"}
    while True:
        choice = input("Select option: ").strip()
        if choice in valid_choices:
            return choice
        print("Invalid choice. Please select from 0 to 6.")


def _prompt_load_on_start(filename: str) -> bool:
    while True:
        choice = input(f"Found {filename}. Load previous records? (y/n): ").strip().lower()
        if choice in {"y", "yes"}:
            return True
        if choice in {"n", "no"}:
            return False
        print("Invalid input. Enter y or n.")


def _prompt_autosave_on_exit(records: list[dict], filename: str) -> None:
    if not records:
        return

    while True:
        choice = input("Save records before exit? (y/n): ").strip().lower()
        if choice in {"y", "yes"}:
            try:
                save_records(records, filename)
                print(f"Records saved to {filename}.")
            except OSError as exc:
                print(f"Could not save records: {exc}")
            return
        if choice in {"n", "no"}:
            print("Exiting without saving.")
            return
        print("Invalid input. Enter y or n.")


def _sanitize_username(username: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9_-]+", "_", username.strip())
    return safe.strip("_-")


def _extract_username_from_path(path: str) -> str | None:
    suffix = "_household_records.txt"
    filename = os.path.basename(path)
    if not filename.endswith(suffix):
        return None
    username = filename[: -len(suffix)]
    return username or None


def _get_existing_usernames() -> list[str]:
    data_dir = "data"
    if not os.path.isdir(data_dir):
        return []

    usernames_by_key: dict[str, str] = {}
    for entry in sorted(os.listdir(data_dir), key=str.lower):
        username = _extract_username_from_path(entry)
        if username is not None:
            usernames_by_key.setdefault(username.lower(), username)
    return list(usernames_by_key.values())


def _prompt_new_username(existing_usernames: list[str]) -> str:
    existing_lookup = {username.lower() for username in existing_usernames}
    while True:
        username = input("Enter username: ").strip()
        if not username:
            print("Username cannot be empty.")
            continue
        safe = _sanitize_username(username)
        if not safe:
            print("Username must include letters or numbers.")
            continue
        if safe.lower() in existing_lookup:
            print("That username already exists. Choose a different one.")
            continue
        return safe


def _user_records_path(username: str) -> str:
    return os.path.join("data", f"{username}_household_records.txt")


def _prompt_existing_user(existing_usernames: list[str]) -> str | None:
    while True:
        print("\nAVAILABLE RECORDS:")
        for index, username in enumerate(existing_usernames, start=1):
            print(f"  [{index}] {username}")
        print("  [0] Back")

        choice = input("\nSelect record to continue: ").strip()
        if choice == "0":
            return None
        try:
            selected_index = int(choice) - 1
        except ValueError:
            print("Invalid choice. Please enter a number from the list.")
            continue

        if 0 <= selected_index < len(existing_usernames):
            return existing_usernames[selected_index]
        print("Invalid choice. Please enter a number from the list.")


def _prompt_startup_user() -> tuple[str, bool]:
    while True:
        existing_usernames = _get_existing_usernames()

        print("\nSTARTUP OPTIONS:")
        print("  [1] Make new record")
        print("  [2] Continue existing record")

        choice = input("\nSelect option: ").strip()
        if choice == "1":
            return _prompt_new_username(existing_usernames), False
        if choice == "2":
            if not existing_usernames:
                print("No existing records found.")
                continue
            username = _prompt_existing_user(existing_usernames)
            if username is None:
                continue
            return username, True
        print("Invalid choice. Please select 1 or 2.")


def _add_appliance_flow(records: list[dict], filename: str) -> None:
    rooms = get_rooms()
    room = display_room_menu(rooms)
    if room is None:
        return

    appliances = get_appliances(room)
    if not appliances:
        print("No appliances available for this room.")
        return

    appliance = display_appliance_menu(appliances)
    if appliance is None:
        return

    usage_level = display_usage_menu()
    hours_per_day = USAGE_LEVELS.get(usage_level)
    if hours_per_day is None:
        print("Invalid usage level selected.")
        return

    try:
        wattage = get_wattage(room, appliance)
    except KeyError:
        print("Selected appliance was not found in the room.")
        return

    record = build_record(room, appliance, wattage, usage_level, hours_per_day)
    records.append(record)

    try:
        save_records(records, filename)
    except OSError as exc:
        records.pop()
        print(f"Failed to save new appliance: {exc}")
        return

    print("Appliance added successfully:")
    print(
        f"  {record['appliance']} in {record['room']} | "
        f"{record['hours_per_day']} hr/day | "
        f"kWh: {record['kwh']:.2f} | "
        f"Monthly Cost: P{record['monthly_cost']:,.2f}"
    )


def _prompt_manage_household_choice() -> str:
    while True:
        print("\nMANAGE HOUSEHOLD:")
        print("  [1] View Current Appliances")
        print("  [2] Add New Appliance")
        print("  [0] Back to Dashboard")

        choice = input("\nSelect option: ").strip()
        if choice in {"0", "1", "2"}:
            return choice
        print("Invalid choice. Please select 0, 1, or 2.")


def _display_current_appliances(records: list[dict]) -> None:
    print("\n" + "-" * 48)
    print(f"{'CURRENT APPLIANCES':^48}")
    print("-" * 48)

    if not records:
        print("No appliances recorded yet.")
    else:
        for index, record in enumerate(records, start=1):
            print(
                f"  {index}. {record.get('appliance', 'Unknown')} | "
                f"Room: {record.get('room', 'Unknown')} | "
                f"Usage: {record.get('usage_level', 'Unknown')} | "
                f"Cost: P{record.get('monthly_cost', 0.0):,.2f}"
            )

    print("-" * 48)
    input("\nPress Enter to return...")


def _manage_household(records: list[dict], filename: str) -> None:
    while True:
        choice = _prompt_manage_household_choice()
        if choice == "1":
            _display_current_appliances(records)
        elif choice == "2":
            _add_appliance_flow(records, filename)
        elif choice == "0":
            return


def main() -> None:
    os.makedirs("data", exist_ok=True)

    username, should_load_existing = _prompt_startup_user()
    filename = _user_records_path(username)

    print(f"Logged in as: {username}")

    records: list[dict] = []
    budget: float | None = None

    if should_load_existing:
        try:
            records = load_records(filename)
            print(f"Loaded {len(records)} record(s).")
        except FileNotFoundError:
            print("Records file not found. Starting with empty records.")
        except Exception as exc:
            print(f"Encountered an issue while loading records: {exc}")
            print("Starting with empty records.")

    while True:
        display_dashboard(records, budget)
        choice = _prompt_main_menu_choice()

        if choice == "1":
            _manage_household(records, filename)
        elif choice == "2":
            if not records:
                print("No records yet.")
            else:
                ranked_appliances = rank_by_appliance(records)
                display_appliance_ranking(ranked_appliances)
        elif choice == "3":
            if not records:
                print("No records yet.")
            else:
                ranked_rooms = rank_by_room(records)
                display_room_ranking(ranked_rooms)
        elif choice == "4":
            budget = prompt_budget()
            total_cost = get_total_cost(records)
            status = check_budget(total_cost, budget)
            print(f"Budget set to P{budget:,.2f}. Status: {status}")
        elif choice == "5":
            try:
                save_records(records, filename)
                print(f"Records saved to {filename}.")
            except OSError as exc:
                print(f"Failed to save records: {exc}")
        elif choice == "6":
            try:
                records = load_records(filename)
                print(f"Loaded {len(records)} record(s).")
            except FileNotFoundError:
                print("No saved records file found.")
            except Exception as exc:
                print(f"Failed to load records: {exc}")
        elif choice == "0":
            _prompt_autosave_on_exit(records, filename)
            print("Thank you for using WattzUp.")
            break


if __name__ == "__main__":
    main()
