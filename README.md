# Project Title

WattzUp: Electricity Consumption Monitoring System

# Group Members

1. Kyle Yuan L. Uy
2. Jefferson S. Magoliman
3. Andrew P. Eroyla
4. Wilbert F. Mijares

# Brief Description

WattzUp is a Python electricity-consumption monitoring application built with an object-oriented architecture. It supports a GUI-first user experience with an optional CLI mode, lets users create or continue per-user sessions, add appliance usage entries by room, estimate monthly electricity cost, view appliance and room rankings, visualize room cost share, review full records with search/filter/sort controls, and manage saved records.

## Context

WattzUp was developed as a practical household energy-tracking system for users who want quick monthly electricity estimates without external APIs or smart-meter integrations. The app is designed around repeatable manual entry, so users can consistently track usage behavior and identify which appliances and rooms drive costs.

The project now runs on a shared object-oriented backend used by both GUI and CLI frontends. This keeps behavior consistent across interfaces, improves maintainability, and makes future feature additions easier.

## Technicals

- Runtime and entrypoints:
  - `main.py` is the primary launcher.
  - Default run mode is GUI (`lib/ui.py`).
  - Optional terminal mode is available via `python main.py --cli`.
  - There is no secondary launcher; `main.py` is the single gateway.
- Architecture (mainly object-oriented):
  - `lib/app.py`: `WattzUpApplicationService` coordinates session state, records, budget, rankings, and persistence.
  - `lib/services.py`: focused domain services for computation, ranking, and budget evaluation.
  - `lib/repository.py`: `HouseholdRecordRepository` handles CSV persistence, loading, sanitization, and validation.
  - `lib/models.py`: shared data model (`ApplianceRecord`) used across layers.
  - `lib/catalog.py` + `util/config.py`: appliance metadata, usage presets, and constants.
  - `lib/ui.py` and `lib/cli_app.py`: interface layers that call the same backend services.
  - Dashboard in `lib/ui.py` includes room donut visualization, actionable insights, and a full records table.
- Data and persistence:
  - Per-user files are stored in `data/` as `<username>_household_records.csv`.
  - Rows are stored in CSV format with typed fields.
  - Malformed rows are skipped on load to avoid crashes.
- Core computation:
  - `kWh = (wattage * hours_per_day * 30) / 1000`
  - `monthly_cost = kWh * rate_per_kwh`
  - Default rate is `12.0` pesos/kWh (`util/config.py`).
  - Usage presets: `Heavy=8`, `Moderate=4`, `Eco=1` hours/day.
- Dependencies:
  - CLI mode uses Python standard library.
  - GUI mode requires `customtkinter` and `Pillow`.
  - Dashboard donut rendering uses `matplotlib` with a built-in textual fallback if unavailable.
  - If GUI dependencies are missing, launcher falls back to CLI.

# Objectives of the Project

1. Build a practical electricity monitoring application for household use.
2. Compute monthly energy consumption and estimated cost using appliance wattage and usage levels.
3. Organize records per user to support separate household tracking sessions.
4. Apply object-oriented design with clear separation of concerns.
5. Provide usable interfaces for adding records, viewing rankings, budget checking, saving, and loading.

# Features and Functionalities

1. Startup flow to create a new user record or continue an existing one.
2. Case-insensitive username validation to prevent duplicate user records (for example, `Jake` and `jake`).
3. Per-user record storage inside the `data/` folder.
4. Household management flow for viewing current appliances and adding new entries.
5. Room and appliance selection menus for record creation.
6. Automatic computation of kWh and monthly electricity cost.
7. Immediate save whenever a new appliance entry is added.
8. Appliance usage ranking based on monthly cost.
9. Room usage ranking based on monthly cost.
10. Dashboard donut chart for room cost share with legend and total cost center label.
11. Dashboard insights module with focus filter (`All`, `Budget`, `Cost Drivers`, `Usage`).
12. Dashboard records table with search, room filter, sort controls, and empty states.
13. Monthly budget input and budget status display.
14. Manual save/load and autosave prompt on exit.

# Programming Concepts Applied

## Object-Oriented (Primary)

The refactored codebase is mainly object-oriented. Core behaviors are encapsulated in classes such as `WattzUpApplicationService`, `EnergyComputationService`, `RankingService`, `BudgetService`, and `HouseholdRecordRepository`. This design separates domain logic, persistence, and interface concerns.

## Functional (Supporting)

The app still uses focused helper-style behaviors (for example, sorting, aggregation, and transformations) where simple function-like logic is appropriate.

## Procedural (Interface Flow)

Menu navigation and user interaction loops in CLI/GUI follow procedural control flow, but these are thin orchestration layers over the object-oriented core.

# Explanation of File Handling Implemented

User records are stored in the `data/` directory, one file per user, using the format `data/<username>_household_records.csv`.

The repository layer writes records as CSV with headers and reads them back as typed model objects. During loading, invalid or incomplete rows are ignored so one bad row does not break the full session load. Username sanitization is also applied before file resolution.

# Instructions of How to Run the Program

1. Open a terminal in the project folder.
2. Run `python main.py` to start the GUI (default mode).
3. If GUI dependencies are not available, run `python main.py --cli` for terminal mode.
4. At startup, create a new user or continue an existing user.
5. Use the dashboard/menu to add appliances, check rankings, set budget, save, load, and exit.
6. On Dashboard, review donut chart, insight cards, and records table controls.

