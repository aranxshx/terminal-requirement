# EXPLANATION.md

## How to Use This Guide
This version is split by ownership task so each developer can focus on one section:
1. Read `Shared Context` once.
2. Go directly to your assigned task section.
3. Use your section's checklist and recitation script for demo prep.

This guide maps legacy ownership in `docs/TASK-OWNERSHIP.md` to the current refactored codebase (`main.py`, `lib/`, `util/`).

## Shared Context (Read Once)

### Current architecture in one view
```text
Interface: lib/ui.py (GUI), lib/cli_app.py (CLI)
    -> Application Orchestrator: lib/app.py
        -> Domain Logic: lib/services.py, lib/catalog.py
            -> Persistence + Model: lib/repository.py, lib/models.py
                -> Constants/Adapters: util/config.py, util/data_layer.py, util/computation.py
```

### Main entrypoint
- Run GUI (default): `python main.py`
- Run CLI: `python main.py --cli`

### Canonical record contract
```python
{
    "room": str,
    "appliance": str,
    "wattage": int,
    "usage_level": str,
    "hours_per_day": int,
    "kwh": float,
    "monthly_cost": float,
}
```

### CSV storage format
- Per-user file: `data/<username>_household_records.csv`
- Columns:
  `room,appliance,wattage,usage_level,hours_per_day,kwh,monthly_cost`

---

## Task 1 Guide: Data Layer (Member 1)

### Legacy ownership mapping
Legacy `data_layer.py` responsibilities now map to:
- `util/config.py` for `APPLIANCE_LIBRARY` and `USAGE_LEVELS`
- `lib/catalog.py` for room/appliance/wattage lookups
- `lib/repository.py` for save/load logic
- `util/data_layer.py` as backward-compatible function adapter

### Fundamentals in this task
- Dictionaries: room -> appliance -> wattage mapping
- Lists: record collections and room/appliance outputs
- File handling: CSV read/write with `csv.DictWriter` and `csv.DictReader`
- Validation: row parsing guards and username sanitization

### Files you own conceptually
- `util/config.py`
- `lib/catalog.py`
- `lib/repository.py`
- `util/data_layer.py`

### Key classes/functions and what they do
- `ApplianceCatalog.rooms()`
  - Returns all room names.
- `ApplianceCatalog.appliances_for_room(room)`
  - Returns appliance names for one room.
- `ApplianceCatalog.wattage_for(room, appliance)`
  - Returns wattage; raises `KeyError` for invalid pair.
- `HouseholdRecordRepository.sanitize_username(username)`
  - Converts username into safe filename fragment.
- `HouseholdRecordRepository.save_for_user(username, records)`
  - Writes records to per-user CSV file.
- `HouseholdRecordRepository.load_for_user(username)`
  - Loads valid rows; silently skips malformed rows.
- `HouseholdRecordRepository._row_to_record(row)`
  - Internal parser/validator for a CSV row.
- Adapter functions in `util/data_layer.py`
  - `get_rooms`, `get_appliances`, `get_wattage`, `save_records`, `load_records`

### Typical call flow
1. UI asks app service for rooms/appliances.
2. App service calls catalog methods.
3. On save/load, app service calls repository methods.
4. Repository reads/writes CSV in `data/`.

### Error handling in your task
- Unknown room/appliance -> `KeyError` (catalog).
- Invalid/missing CSV values -> row skipped (`_row_to_record` returns `None`).
- Missing user file -> empty list returned by `load_for_user`.
- Invalid username input -> sanitized/validated before file path use.

### Common mistakes and quick checks
- Mistake: Changing CSV columns without updating repository `_FIELDNAMES`.
- Mistake: Assuming `.txt` instead of `.csv` suffix.
- Check: save, reopen app, continue user, verify rows load.
- Check: inject one corrupted row and ensure load does not crash.

### 60-90 second recitation script
I handle the data layer. Static system data like appliance wattage and usage presets is in `util/config.py`. Lookup operations are in `lib/catalog.py`. Persistence is in `lib/repository.py`, where each user gets a CSV file in the `data` folder. I also handle data safety through username sanitization and row-level validation. Invalid CSV rows are skipped so one bad line does not crash loading.

---

## Task 2 Guide: Computation Engine (Member 2)

### Legacy ownership mapping
Legacy `computation.py` responsibilities now map to:
- `lib/services.py` as core implementation
- `util/computation.py` as backward-compatible adapter

### Fundamentals in this task
- Arithmetic formulas for kWh and monthly cost
- Aggregation/sorting for rankings
- Conditional logic for budget evaluation
- Rounding with `round(value, 2)`

### Files you own conceptually
- `lib/services.py`
- `util/computation.py`
- Reference constants from `util/config.py`

### Key classes/functions and what they do
- `EnergyComputationService.build_record(room, appliance, wattage, usage_level)`
  - Computes:
    - `kWh = (wattage * hours_per_day * 30) / 1000`
    - `monthly_cost = kWh * rate_per_kwh`
  - Returns `ApplianceRecord`.
  - Raises `ValueError` for unknown usage level.
- `EnergyComputationService.total_cost(records)`
  - Returns total `monthly_cost`.
- `RankingService.rank_appliances(records)`
  - Sorts records descending by `monthly_cost`.
- `RankingService.rank_rooms(records)`
  - Groups by room, sums costs, sorts descending.
- `BudgetService.budget_status(total_cost, budget)`
  - Returns `NOT SET`, `UNDER BUDGET`, or `OVER BUDGET`.
- Adapter functions in `util/computation.py`
  - `compute_cost`, `build_record`, `get_total_cost`, `rank_by_room`, `rank_by_appliance`, `check_budget`

### Typical call flow
1. App service receives add request.
2. App service asks catalog for wattage.
3. Computation service builds typed record.
4. Ranking/budget methods are called during dashboard and report views.

### Error handling in your task
- Unknown usage level -> `ValueError`.
- Invalid adapter payload -> `from_dict` conversions can raise parsing errors upstream.

### Common mistakes and quick checks
- Mistake: inconsistent rounding precision.
- Mistake: mixing legacy budget text (`No budget set`) with current (`NOT SET`).
- Check: verify known sample result (400W, Moderate=4h, rate=12 => 48kWh, 576 cost).
- Check: verify rank order with two known records.

### 60-90 second recitation script
I handle the computation engine in `lib/services.py`. The energy service computes kWh and monthly cost from wattage and usage level. The ranking service returns appliance and room rankings based on monthly cost. The budget service compares total cost against user budget and returns a clear status. This logic is UI-independent, so both CLI and GUI use exactly the same math.

---

## Task 3 Guide: UI Layer (Member 3)

### Legacy ownership mapping
Legacy `ui.py` display/menu responsibilities now map to:
- `lib/cli_app.py` for terminal interaction
- `lib/ui.py` for GUI interaction

### Fundamentals in this task
- Input/output handling
- Menu/navigation loops (CLI)
- Event-driven callbacks (GUI)
- Display formatting and user messaging

### Files you own conceptually
- `lib/cli_app.py`
- `lib/ui.py`

### Key classes/functions and what they do
- `WattzUpCLI.run()`
  - Main CLI dashboard loop.
- `WattzUpCLI._startup_flow()`
  - New user vs continue existing user flow.
- `WattzUpCLI._add_appliance_flow()`
  - Room -> appliance -> usage -> add record.
- `WattzUpCLI._show_appliance_ranking()` / `_show_room_ranking()`
  - Ranking display screens.
- `WattzUpCLI._set_budget()`
  - Budget prompt and validation loop.
- `WattzUpVisual.__init__()`
  - Builds GUI frame layout, starts login flow.
- `WattzUpVisual._login_user()`
  - User session choice via dialogs.
- `WattzUpVisual._add_entry(...)`
  - Adds record from selected room/appliance/usage.
- `WattzUpVisual._show_map()`
  - Dashboard summary and room hotspots.
- `WattzUpVisual._save_data()` / `_on_window_close()`
  - Save and exit behaviors.

### Typical call flow
1. UI collects user choices.
2. UI calls `WattzUpApplicationService` methods.
3. UI displays resulting totals/rankings/status.
4. UI handles recoverable errors without crashing.

### Error handling in your task
- CLI invalid numeric/menu input -> re-prompt loops.
- GUI invalid actions -> `messagebox.showerror` and return.
- App-level exceptions are caught in UI and shown cleanly.

### Common mistakes and quick checks
- Mistake: putting business logic directly in UI methods.
- Mistake: mutating `records` directly instead of using app service.
- Check: test new-user and continue-user paths separately.
- Check: test cancel/close actions in dialogs.

### 60-90 second recitation script
I handle the UI layer. The CLI is in `lib/cli_app.py` and the GUI is in `lib/ui.py`. Both interfaces collect input, call the same app service, and display results. This keeps behavior consistent across interfaces. The UI layer focuses on prompts, navigation, and feedback, while computation and persistence stay in backend modules.

---

## Task 4 Guide: Integration, Main Flow, and Error Handling (Member 4)

### Legacy ownership mapping
Legacy `wattzup.py` integration and main-loop ownership now maps to:
- `main.py` as single gateway
- `lib/app.py` as core orchestration service
- `lib/cli_app.py` and `lib/ui.py` as integrated interface flows

### Fundamentals in this task
- Program entrypoints and argument parsing
- Dependency wiring and orchestration
- Cross-layer error handling
- End-to-end flow validation

### Files you own conceptually
- `main.py`
- `lib/app.py`
- Integration touchpoints in `lib/cli_app.py` and `lib/ui.py`

### Key classes/functions and what they do
- `main._build_parser()`
  - Defines CLI flags (`--cli`).
- `main.run_cli()`
  - Builds default service and starts CLI runner.
- `main.run_gui()`
  - Imports GUI, builds default service, starts mainloop.
  - Raises `RuntimeError` when GUI deps are unavailable.
- `main.main()`
  - Chooses mode and handles GUI fallback to CLI.
- `create_default_application_service()`
  - Wires repository, catalog, and domain services.
- `WattzUpApplicationService` methods:
  - Session: `create_new_user_session`, `continue_user_session`
  - Records: `add_appliance_usage`, `clear_records`
  - Persistence: `save_current_session`, `load_current_session`
  - Reporting: `total_cost`, `ranked_appliances`, `ranked_rooms`, `budget_status`

### End-to-end integrated flow
1. User starts app through `main.py`.
2. Launcher selects GUI by default or CLI via `--cli`.
3. UI starts/continues session through app service.
4. Add flow calls catalog + computation service + repository save.
5. Rankings and budget checks use service layer methods.
6. Exit path offers save behavior via UI/CLI hooks.

### Error handling ownership map
- GUI dependency missing -> handled in `main.py` by CLI fallback.
- Invalid username / duplicate user -> raised in app service, shown by UI.
- No active session save/load -> `RuntimeError` from app service.
- Invalid room/appliance or usage -> `KeyError`/`ValueError` caught in UI.
- Malformed CSV rows -> skipped in repository parser.
- Invalid CLI input -> loop and re-prompt in `lib/cli_app.py`.

### Common mistakes and quick checks
- Mistake: bypassing `create_default_application_service` wiring.
- Mistake: inconsistent exception messages across UI/CLI.
- Check: run both `python main.py` and `python main.py --cli`.
- Check: verify autosave or save prompt on exit paths.

### 60-90 second recitation script
I handle integration and reliability. `main.py` is the single gateway and controls mode selection. `lib/app.py` is the orchestrator that connects catalog, services, and repository into one workflow. I ensure the end-to-end flow works from session start to add, rank, budget, save, and exit. I also ensure error handling is graceful, including invalid input, bad records, and GUI fallback to CLI.

---

## Shared Testing Checklist (All Members)

### Core behavior
- Launch GUI: `python main.py`
- Launch CLI: `python main.py --cli`
- Create user, add records, save, restart, continue user, verify reload.

### Data layer checks
- Confirm per-user CSV file naming.
- Confirm malformed CSV row is skipped, not crashing load.

### Computation checks
- Verify known formula result for 400W, Moderate, rate 12.
- Verify ranking order and room aggregation are descending.

### UI checks
- Confirm CLI re-prompts on invalid input.
- Confirm GUI shows dialogs for invalid actions and save prompts.

### Integration checks
- Confirm CLI fallback if GUI deps are unavailable.
- Confirm app handles missing session actions with user-facing errors.

## Where to Extend Next
1. Add unit tests for repository parsing and service math.
2. Add user-configurable electricity rate persistence.
3. Add richer analytics (monthly trends and comparisons).
4. Add optional warning logs for skipped malformed rows.
