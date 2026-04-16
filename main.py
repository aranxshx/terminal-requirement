"""
Main loop, integration, and error handling for WattzUp.
Member 4 deliverable before final single-file merge.
"""

from __future__ import annotations

import os
import re

from computation import build_record, get_total_cost, rank_by_appliance, rank_by_room
from data_layer import (
    USAGE_LEVELS,
    get_appliances,
    get_rooms,
    get_wattage,
    load_records,
    save_records,
)
from UI import (
    display_appliance_menu,
    display_appliance_ranking,
    display_dashboard,
    display_room_menu,
    display_room_ranking,
    display_usage_menu,
    prompt_budget,
)


def clear_records(records: list[dict]) -> list[dict]:
    """Reset records after user confirmation."""
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
    """Prompt until the user selects a valid dashboard menu option."""
    valid_choices = {"0", "1", "2", "3", "4", "5", "6", "7"}
    while True:
        choice = input("Select option: ").strip()
        if choice in valid_choices:
            return choice
        print("Invalid choice. Please select from 0 to 7.")


def _prompt_load_on_start(filename: str) -> bool:
    """Ask whether previous records should be loaded if a file exists."""
    while True:
        choice = input(f"Found {filename}. Load previous records? (y/n): ").strip().lower()
        if choice in {"y", "yes"}:
            return True
        if choice in {"n", "no"}:
            return False
        print("Invalid input. Enter y or n.")


def _prompt_autosave_on_exit(records: list[dict], filename: str) -> None:
    """Ask to save records before exiting the program."""
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
    """Convert username into a safe filename fragment."""
    safe = re.sub(r"[^A-Za-z0-9_-]+", "_", username.strip())
    return safe.strip("_-")


def _extract_username_from_path(path: str) -> str | None:
    """Extract the stored username from a records filename."""
    suffix = "_household_records.txt"
    filename = os.path.basename(path)
    if not filename.endswith(suffix):
        return None
    username = filename[: -len(suffix)]
    return username or None


def _get_existing_usernames() -> list[str]:
    """Return stored usernames from the data directory."""
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
    """Prompt until a unique username is provided."""
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
    """Build per-user records path inside the data directory."""
    return os.path.join("data", f"{username}_household_records.txt")


def _prompt_existing_user(existing_usernames: list[str]) -> str | None:
    """Display available users and prompt for one to continue."""
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
    """Ask whether to create a new user record or continue an existing one."""
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
    """Collect one appliance entry and append a computed record."""
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
    """Prompt for a household management action."""
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
    """Show current appliance records for the logged-in user."""
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
    """Handle the manage household submenu."""
    while True:
        choice = _prompt_manage_household_choice()
        if choice == "1":
            _display_current_appliances(records)
        elif choice == "2":
            _add_appliance_flow(records, filename)
        elif choice == "0":
            return


def main() -> None:
    """Program entry point for WattzUp integration flow."""
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
        except Exception as exc:  # pragma: no cover - defensive fallback
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
            print(f"Budget set to P{budget:,.2f}. Current total is P{total_cost:,.2f}.")
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
            except Exception as exc:  # pragma: no cover - defensive fallback
                print(f"Failed to load records: {exc}")
        elif choice == "7":
            records = clear_records(records)
        elif choice == "0":
            _prompt_autosave_on_exit(records, filename)
            print("Thank you for using WattzUp.")
            break


if __name__ == "__main__":
    main()
