"""
Main loop, integration, and error handling for WattzUp.
Member 4 deliverable before final single-file merge.
"""

from __future__ import annotations

import os

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


def _add_appliance_flow(records: list[dict]) -> None:
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

    print("Appliance added successfully:")
    print(
        f"  {record['appliance']} in {record['room']} | "
        f"{record['hours_per_day']} hr/day | "
        f"kWh: {record['kwh']:.2f} | "
        f"Monthly Cost: P{record['monthly_cost']:,.2f}"
    )


def main() -> None:
    """Program entry point for WattzUp integration flow."""
    filename = "household_records.txt"
    records: list[dict] = []
    budget: float | None = None

    if os.path.exists(filename):
        if _prompt_load_on_start(filename):
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
            _add_appliance_flow(records)
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
