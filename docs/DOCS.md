# Project Title

WattzUp: Electricity Consumption Monitoring System

# Group Members

1. [Member 1 Name]
2. [Member 2 Name]
3. [Member 3 Name]
4. [Member 4 Name]

# Brief Description

WattzUp is a Python terminal-based application for monitoring household electricity consumption. It allows a user to create or continue a personal record, add appliance usage entries by room, estimate monthly electricity cost, view rankings for appliances and rooms, and manage saved records per user.

# Objectives of the Project

1. Build a practical terminal program for tracking household electricity usage.
2. Compute monthly energy consumption and estimated cost based on appliance wattage and usage level.
3. Organize appliance records per user so different users can keep separate data.
4. Apply core Python concepts such as functions, control flow, file handling, and input validation.
5. Provide a clear interface for household management, rankings, budget status, saving, and loading.

# Features and Functionalities

1. Startup flow to create a new user record or continue an existing one.
2. Case-insensitive username validation to prevent duplicate records such as `Jake` and `jake`.
3. Per-user record storage inside the `data/` folder.
4. Manage Household submenu for viewing appliances and adding new records.
5. Room and appliance selection menus for entering appliance usage records.
6. Usage-level input (`Heavy`, `Moderate`, `Eco`) mapped to fixed hours/day.
7. Automatic computation of kWh and monthly electricity cost.
8. Automatic save after adding a new appliance record.
9. Appliance usage ranking based on monthly cost.
10. Room usage ranking based on monthly cost.
11. Monthly budget input and budget status display (`UNDER BUDGET` / `OVER BUDGET`).
12. Manual save, manual load, and autosave prompt on exit.

# System Flow Summary

1. User starts the program.
2. User selects startup option:
   - Make new record
   - Continue existing record
3. Program enters dashboard loop.
4. User chooses dashboard actions:
   - Manage Household
   - View Appliance Usage Ranking
   - View Room Usage Ranking
   - Set Monthly Budget
   - Save Records
   - Load Records
   - Exit
5. Program optionally autosaves on exit.

# Rooms and Appliance Library

The current appliance library includes fixed rooms and predefined wattages.

## Bathroom
- Lights — 15 W
- Hair Dryer — 1200 W
- Charger — 10 W
- Water Heater — 2000 W

## Kitchen
- Rice Cooker — 400 W
- Electric Kettle — 1500 W
- Electric Stove — 1000 W
- Dishwasher — 1800 W
- Lights — 15 W
- Fan — 60 W
- Water Dispenser — 500 W

## Dining Area
- Fan — 60 W
- Lights — 15 W
- Charger — 10 W
- Aircon — 1500 W

## Living Room
- TV — 150 W
- Aircon — 1500 W
- Fan — 60 W
- Lights — 15 W
- Charger — 10 W

## Bedroom
- Charger — 10 W
- Lights — 15 W
- Aircon — 1500 W
- Fan — 60 W
- Lamp — 40 W

# Computation Logic

## Usage-Level Mapping

- Heavy = 8 hours/day
- Moderate = 4 hours/day
- Eco = 1 hour/day

## Formulas

- `kWh per month = (Wattage × Hours per Day × 30) / 1000`
- `Monthly Cost = kWh × Rate per kWh`

Default rate used in the code is `12.0` pesos per kWh.

# Record Data Contract

Each appliance record is stored as a dictionary with this format:

1. `room` (str)
2. `appliance` (str)
3. `wattage` (int)
4. `usage_level` (str)
5. `hours_per_day` (int)
6. `kwh` (float)
7. `monthly_cost` (float)

# File Handling Implemented

The system uses CSV-style text files stored in the `data/` folder.

## File Naming

- One file per user:
  - `data/<username>_household_records.txt`

## Save Behavior

1. Writes a CSV header.
2. Writes one line per record.
3. Creates the folder path when needed.

## Load Behavior

1. Reads file line by line.
2. Skips blank lines.
3. Skips malformed lines (wrong columns, invalid numeric values, invalid usage level, negative values).
4. Ignores CSV header when parsing.
5. Returns only valid records.

# Error Handling Summary

The program handles common error cases without crashing:

1. Non-numeric menu input.
2. Out-of-range menu selection.
3. Empty username input.
4. Unsafe/invalid username after sanitization.
5. Duplicate username check (case-insensitive).
6. Invalid budget input (non-numeric or negative).
7. Missing records file on load.
8. File save/load operation errors (`OSError`).
9. Missing room/appliance key lookup fallback during add flow.
10. Empty records state in ranking and appliance list views.

# Programming Concepts Applied

## Data Types

- `int`: wattage and hours/day
- `float`: kWh, monthly cost, budget
- `str`: room names, appliance names, usage level, user input
- `bool` and nullable values: startup decisions and budget state

## Operators

- Arithmetic operators for cost calculations
- Comparison operators for menu validation and budget checks

## Control Structures

- `if / elif / else` for branching logic
- `while` loops for menu prompting and validation
- `for` loops for ranking and display iteration

## Functions and Modularity

The project is separated into functional areas:

1. Data layer (appliance library, save/load, parsing)
2. Computation layer (cost calculation, total, rankings)
3. UI layer (dashboard and menus)
4. Main loop (workflow integration and orchestration)

## File Handling

- Persistent storage using per-user text files
- CSV writer for save operations
- Line parser and validation for load operations

## Error Handling

- `try/except` for numeric conversion and file operations
- Defensive checks before processing user and record data

# Project Structure

- `wattzup.py` — final merged single-file program
- `main.py` — modular main integration flow
- `data_layer.py` — appliance library, parsing, save/load
- `computation.py` — formulas, totals, rankings, budget check
- `UI.py` — display functions and menu input prompts
- `data/` — saved user record files
- `docs/documentation.txt` — short documentation version

# How to Run the Program

1. Open a terminal in the project folder.
2. Run `python wattzup.py`.
3. Select startup option (new record or continue record).
4. Use dashboard options to manage appliances, view rankings, set budget, save/load, or exit.
5. On exit, choose whether to autosave.

# Notes and Limitations

1. The current appliance list and wattage values are predefined in code.
2. The monthly cost formula uses a fixed default electricity rate unless changed in code.
3. Saved files are local text files; no cloud/database integration is included.
4. The interface is terminal-based and designed for simplicity and clarity.
