from __future__ import annotations

from lib.app import WattzUpApplicationService
from util.config import USAGE_LEVELS


class WattzUpCLI:
    """Terminal UI runner for WattzUp using the shared application service."""

    def __init__(self, application_service: WattzUpApplicationService) -> None:
        self._app = application_service

    def run(self) -> None:
        username = self._startup_flow()
        print(f"Logged in as: {username}")

        while True:
            self._display_dashboard()
            choice = self._prompt_menu_choice({"0", "1", "2", "3", "4", "5", "6", "7"})

            if choice == "1":
                self._manage_household()
            elif choice == "2":
                self._show_appliance_ranking()
            elif choice == "3":
                self._show_room_ranking()
            elif choice == "4":
                self._set_budget()
            elif choice == "5":
                self._save_records()
            elif choice == "6":
                self._load_records()
            elif choice == "7":
                self._clear_records()
            elif choice == "0":
                self._prompt_autosave_on_exit()
                print("Thank you for using WattzUp.")
                return

    def _startup_flow(self) -> str:
        while True:
            existing_users = self._app.list_existing_users()

            print("\nSTARTUP OPTIONS:")
            print("  [1] Make new record")
            print("  [2] Continue existing record")
            choice = self._prompt_menu_choice({"1", "2"})

            if choice == "1":
                username = input("Enter username: ").strip()
                try:
                    return self._app.create_new_user_session(username)
                except ValueError as exc:
                    print(exc)
                    continue

            if not existing_users:
                print("No existing records found.")
                continue

            selected_user = self._prompt_existing_user(existing_users)
            if selected_user is None:
                continue

            return self._app.continue_user_session(selected_user)

    def _prompt_existing_user(self, existing_users: list[str]) -> str | None:
        while True:
            print("\nAVAILABLE RECORDS:")
            for index, username in enumerate(existing_users, start=1):
                print(f"  [{index}] {username}")
            print("  [0] Back")

            choice = input("\nSelect record to continue: ").strip()
            if choice == "0":
                return None

            try:
                index = int(choice) - 1
            except ValueError:
                print("Invalid choice. Please enter a number from the list.")
                continue

            if 0 <= index < len(existing_users):
                return existing_users[index]

            print("Invalid choice. Please enter a number from the list.")

    def _display_dashboard(self) -> None:
        total_cost = self._app.total_cost()
        status = "NO RECORDS YET" if not self._app.records else self._app.budget_status()

        print("\n" + "=" * 76)
        print("WATTZUP DASHBOARD")
        print("=" * 76)
        print(f"Estimated Monthly Cost : P{total_cost:,.2f}")
        print(f"Budget Status          : {status}")
        print("\n[1] Manage Household")
        print("[2] View Appliance Usage Ranking")
        print("[3] View Room Usage Ranking")
        print("[4] Set Monthly Budget")
        print("[5] Save Records")
        print("[6] Load Records")
        print("[7] Clear Records")
        print("[0] Exit")
        print("=" * 76)

    def _manage_household(self) -> None:
        while True:
            print("\nMANAGE HOUSEHOLD:")
            print("  [1] View Current Appliances")
            print("  [2] Add New Appliance")
            print("  [0] Back to Dashboard")

            choice = self._prompt_menu_choice({"0", "1", "2"})
            if choice == "1":
                self._display_current_appliances()
            elif choice == "2":
                self._add_appliance_flow()
            else:
                return

    def _display_current_appliances(self) -> None:
        print("\n" + "-" * 60)
        print("CURRENT APPLIANCES")
        print("-" * 60)

        if not self._app.records:
            print("No appliances recorded yet.")
        else:
            for index, record in enumerate(self._app.records, start=1):
                print(
                    f"{index}. {record.appliance} | Room: {record.room} | "
                    f"Usage: {record.usage_level} | Cost: P{record.monthly_cost:,.2f}"
                )

        print("-" * 60)
        input("\nPress Enter to return...")

    def _add_appliance_flow(self) -> None:
        room = self._prompt_room_selection()
        if room is None:
            return

        appliance = self._prompt_appliance_selection(room)
        if appliance is None:
            return

        usage_level = self._prompt_usage_level()
        try:
            record = self._app.add_appliance_usage(room, appliance, usage_level)
        except (ValueError, KeyError, RuntimeError) as exc:
            print(f"Could not add appliance: {exc}")
            return

        print("Appliance added successfully:")
        print(
            f"  {record.appliance} in {record.room} | {record.hours_per_day} hr/day | "
            f"kWh: {record.kwh:.2f} | Monthly Cost: P{record.monthly_cost:,.2f}"
        )

    def _prompt_room_selection(self) -> str | None:
        rooms = self._app.catalog.rooms()
        while True:
            print("\nSELECT ROOM:")
            for index, room in enumerate(rooms, start=1):
                print(f"  [{index}] {room}")
            print("  [0] Back")

            choice = input("\nEnter choice: ").strip()
            if choice == "0":
                return None

            try:
                index = int(choice) - 1
            except ValueError:
                print("Error: Please enter a valid number.")
                continue

            if 0 <= index < len(rooms):
                return rooms[index]

            print("Invalid choice. Please select from the list.")

    def _prompt_appliance_selection(self, room: str) -> str | None:
        appliances = self._app.catalog.appliances_for_room(room)
        while True:
            print("\nSELECT APPLIANCE:")
            for index, appliance in enumerate(appliances, start=1):
                print(f"  [{index}] {appliance}")
            print("  [0] Back")

            choice = input("\nEnter choice: ").strip()
            if choice == "0":
                return None

            try:
                index = int(choice) - 1
            except ValueError:
                print("Error: Please enter a valid number.")
                continue

            if 0 <= index < len(appliances):
                return appliances[index]

            print("Invalid choice. Please select from the list.")

    def _prompt_usage_level(self) -> str:
        while True:
            print("\nHOW OFTEN DO YOU USE THIS APPLIANCE?")
            print("  [1] Heavy    - 8+ hours/day")
            print("  [2] Moderate - 2 to 8 hours/day")
            print("  [3] Eco      - Less than 2 hours/day")

            mapping = {"1": "Heavy", "2": "Moderate", "3": "Eco"}
            choice = input("\nEnter choice: ").strip()
            if choice in mapping:
                return mapping[choice]

            print("Invalid choice. Please select 1, 2, or 3.")

    def _show_appliance_ranking(self) -> None:
        ranked = self._app.ranked_appliances()
        print("\n" + "-" * 50)
        print("APPLIANCE USAGE RANKING")
        print("-" * 50)

        if not ranked:
            print("No data available.")
        else:
            for index, record in enumerate(ranked, start=1):
                print(f"{index}. {record.appliance} ({record.room}) - P{record.monthly_cost:,.2f}")

        print("-" * 50)
        input("\nPress Enter to return to Dashboard...")

    def _show_room_ranking(self) -> None:
        ranked = self._app.ranked_rooms()
        print("\n" + "-" * 40)
        print("ROOM USAGE RANKING")
        print("-" * 40)

        if not ranked:
            print("No data available.")
        else:
            for index, (room, cost) in enumerate(ranked, start=1):
                print(f"{index}. {room:<20} P{cost:,.2f}")

        print("-" * 40)
        input("\nPress Enter to return to Dashboard...")

    def _set_budget(self) -> None:
        while True:
            raw_value = input("\nEnter monthly budget in pesos (P): ").replace(",", "").strip()
            try:
                budget = float(raw_value)
                self._app.set_budget(budget)
            except ValueError:
                print("Error: Invalid amount. Please enter numbers only.")
                continue

            print(f"Budget set to P{budget:,.2f}. Current total is P{self._app.total_cost():,.2f}.")
            return

    def _save_records(self) -> None:
        try:
            self._app.save_current_session()
        except RuntimeError as exc:
            print(exc)
            return

        print("Records saved successfully.")

    def _load_records(self) -> None:
        try:
            self._app.load_current_session()
        except RuntimeError as exc:
            print(exc)
            return

        print(f"Loaded {len(self._app.records)} record(s).")

    def _clear_records(self) -> None:
        while True:
            choice = input("Are you sure you want to clear all records? (y/n): ").strip().lower()
            if choice in {"y", "yes"}:
                self._app.clear_records()
                print("All records have been cleared.")
                return
            if choice in {"n", "no"}:
                print("Clear canceled.")
                return
            print("Invalid input. Enter y or n.")

    def _prompt_autosave_on_exit(self) -> None:
        if not self._app.records:
            return

        while True:
            choice = input("Save records before exit? (y/n): ").strip().lower()
            if choice in {"y", "yes"}:
                self._save_records()
                return
            if choice in {"n", "no"}:
                print("Exiting without saving.")
                return
            print("Invalid input. Enter y or n.")

    @staticmethod
    def _prompt_menu_choice(valid_choices: set[str]) -> str:
        while True:
            choice = input("Select option: ").strip()
            if choice in valid_choices:
                return choice
            allowed = ", ".join(sorted(valid_choices))
            print(f"Invalid choice. Please select from {allowed}.")
