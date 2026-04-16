"""
WattzUp: Electricity Consumption Monitoring System
Member 3: User Interface (Menus, Display & Navigation)
"""

def display_dashboard(records, budget):
    """Shows the main dashboard header, costs, and menu."""
    total_cost = sum(record.get('MonthlyCost', 0) for record in records)
    
    print("\n" + "=" * 41)
    print(f"{'WATTZUP — DASHBOARD':^41}")
    print("=" * 41)
    
    if not records:
        print("  Estimated Monthly Cost : ₱0.00")
        print("  Budget Status          : NO RECORDS YET")
    else:
        print(f"  Estimated Monthly Cost : ₱{total_cost:,.2f}")
        
        if budget == 0:
            print("  Budget Status          : NOT SET")
        elif total_cost > budget:
            print("  Budget Status          : OVER BUDGET ✗")
        else:
            print("  Budget Status          : UNDER BUDGET ✓")

    print("\n  [1] Manage Household")
    print("  [2] View Appliance Usage Ranking")
    print("  [3] View Room Usage Ranking")
    print("  [4] Set Monthly Budget")
    print("  [5] Save Records")
    print("  [6] Load Records")
    print("  [0] Exit")
    print("=" * 41)


def display_room_menu(rooms):
    """Shows numbered list of rooms and returns the selection."""
    while True:
        print("\nSELECT ROOM:")
        for i, room in enumerate(rooms, 1):
            print(f"  [{i}] {room}")
        print("  [0] Back")
        
        choice = input("\nEnter choice: ")
        if choice == '0':
            return None
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(rooms):
                return rooms[idx]
            else:
                print("Invalid choice. Please select from the list.")
        except ValueError:
            print("Error: Please enter a valid number.")


def display_appliance_menu(appliances):
    """Shows numbered list of appliances for the selected room."""
    while True:
        print("\nSELECT APPLIANCE:")
        for i, app in enumerate(appliances, 1):
            print(f"  [{i}] {app['name']} ({app['wattage']}W)")
        print("  [0] Back")
        
        choice = input("\nEnter choice: ")
        if choice == '0':
            return None
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(appliances):
                return appliances[idx]
            else:
                print("Invalid choice.")
        except ValueError:
            print("Error: Please enter a valid number.")


def display_usage_menu():
    """Shows usage level options and returns selection."""
    while True:
        print("\nHOW OFTEN DO YOU USE THIS APPLIANCE?")
        print("  [1] Heavy   — 8+ hours/day")
        print("  [2] Moderate — 2 to 8 hours/day")
        print("  [3] Eco      — Less than 2 hours/day")
        
        choice = input("\nEnter choice: ")
        mapping = {"1": "Heavy", "2": "Moderate", "3": "Eco"}
        
        if choice in mapping:
            return mapping[choice]
        print("Invalid choice. Please select 1, 2, or 3.")


def display_room_ranking(ranked_rooms):
    """Shows rooms ranked by cost. ranked_rooms: list of (room_name, cost) tuples."""
    print("\n" + "-" * 30)
    print(f"{'ROOM USAGE RANKING':^30}")
    print("-" * 30)
    if not ranked_rooms:
        print("No data available.")
    else:
        for i, (room, cost) in enumerate(ranked_rooms, 1):
            print(f"  {i}. {room:<15} : ₱{cost:,.2f}")
    print("-" * 30)
    input("\nPress Enter to return to Dashboard...")


def display_appliance_ranking(ranked_appliances):
    """Shows appliances ranked by cost. ranked_appliances: list of dictionaries."""
    print("\n" + "-" * 40)
    print(f"{'APPLIANCE USAGE RANKING':^40}")
    print("-" * 40)
    if not ranked_appliances:
        print("No data available.")
    else:
        for i, app in enumerate(ranked_appliances, 1):
            name_str = f"{app['Appliance']} ({app['Room']})"
            print(f"  {i}. {name_str:<22} : ₱{app['MonthlyCost']:,.2f}")
    print("-" * 40)
    input("\nPress Enter to return to Dashboard...")


def prompt_budget():
    """Prompts for monthly budget and returns float."""
    while True:
        try:
            val = input("\nEnter monthly budget in pesos (₱): ").replace(',', '')
            budget = float(val)
            if budget < 0:
                print("Budget cannot be negative.")
                continue
            return budget
        except ValueError:
            print("Error: Invalid amount. Please enter numbers only.")