# EXPLANATION.md

## How to Use This Guide
Use this file in three passes:
1. Read Project Orientation and Architecture Overview to understand the system shape.
2. Read File-by-File Guide and Class/Function Reference to understand implementation details.
3. Use End-to-End Flows, Error Handling, and Testing Checklist to prepare for demos, recitations, and debugging.

This guide is aligned to the current refactored codebase and the legacy ownership plan in docs/TASK-OWNERSHIP.md.

## Project Orientation

### What the app does
WattzUp tracks household electricity usage per user. A user can:
- create or continue a profile,
- add appliance usage entries per room,
- see estimated monthly costs,
- view appliance and room rankings,
- set a monthly budget,
- save and load records from CSV files.

### Why it exists
The original class requirement focused on Python fundamentals (data structures, control flow, file handling, validation). The refactored version keeps those fundamentals but organizes them into maintainable object-oriented modules so behavior is shared across GUI and CLI.

### High-level architecture in plain English
The interface layer (GUI or CLI) collects user input and shows results. It calls one application service that manages session state and orchestrates operations. The application service uses domain services for computation/ranking/budget checks, a repository for CSV persistence, a model for typed records, and a config catalog for static data.

## Architecture Overview

### Layered diagram

```text
+-----------------------------+
| Interface Layer             |
| - lib/ui.py (GUI)           |
| - lib/cli_app.py (CLI)      |
+-------------+---------------+
              |
              v
+-----------------------------+
| Application Layer           |
| - lib/app.py                |
|   WattzUpApplicationService |
+-------------+---------------+
              |
              v
+-----------------------------+
| Domain Services Layer       |
| - lib/services.py           |
|   Energy, Ranking, Budget   |
+-------------+---------------+
              |
      +-------+-------+
      v               v
+------------+   +----------------+
| Repository |   | Domain Model   |
| lib/repository.py               |
| HouseholdRecordRepository       |
|            |   | lib/models.py  |
|            |   | ApplianceRecord|
+------------+   +----------------+
      |
      v
+-----------------------------+
| Config and Data Contracts   |
| - util/config.py            |
| - util/data_layer.py        |
| - util/computation.py       |
+-----------------------------+
```

### Responsibilities and boundaries per layer
| Layer | Owns | Does not own |
|---|---|---|
| Interface | Input prompts, display, user interaction loops | Business math formulas, CSV parsing rules |
| Application | Session lifecycle, orchestration, calling services/repository | Rendering widgets/menus, low-level file parsing |
| Domain services | Cost math, ranking logic, budget decision rules | File writes, UI prompts |
| Repository/model | CSV read/write and validation, typed record conversion | Menu flow and display decisions |
| Config/util adapters | Constants and backward-compatible function APIs | Frontend orchestration |

### Why separation matters
- Reuse: GUI and CLI share the same backend behavior.
- Testability: Services and repository can be tested without running UI.
- Maintainability: changes in one area (for example, ranking) stay local.
- Recitation clarity: ownership areas map cleanly to code modules.

## Task Ownership Mapping (Legacy -> Current)

The ownership plan in docs/TASK-OWNERSHIP.md describes a procedural, single-file merge target. The current codebase keeps the same responsibilities but redistributes them into classes and modules.

| Legacy ownership area | Legacy functions/files | Current equivalent |
|---|---|---|
| Part 1 Data Layer (Member 1) | data_layer.py with APPLIANCE_LIBRARY, USAGE_LEVELS, save_records, load_records, getters | util/config.py constants, lib/catalog.py (rooms/appliances/wattage), lib/repository.py (save_for_user/load_for_user), util/data_layer.py adapter |
| Part 2 Computation (Member 2) | computation.py with compute_cost/build_record/total/rank/check_budget | lib/services.py with EnergyComputationService, RankingService, BudgetService, util/computation.py adapter |
| Part 3 UI (Member 3) | ui.py display functions and prompts | lib/cli_app.py (CLI class methods), lib/ui.py (GUI class methods) |
| Part 4 Integration (Member 4) | main loop in wattzup.py | main.py launcher, lib/app.py orchestration service, lib/cli_app.py loop, lib/ui.py window lifecycle |

### Renamed, moved, or refactored items
| Legacy item | Current status |
|---|---|
| household_records.csv generic file | now per-user files in data/<username>_household_records.csv |
| Procedural save_records/load_records as core implementation | now adapters in util/data_layer.py; core implementation moved to lib/repository.py |
| Procedural compute_* and ranking functions as core implementation | now adapters in util/computation.py; core implementation moved to lib/services.py |
| Single-file integration in wattzup.py | replaced by modular launcher in main.py and package modules under lib/ and util/ |

### Old function style vs current class/service methods
- get_rooms, get_appliances, get_wattage
  - old: direct functions in data_layer.py
  - current: ApplianceCatalog.rooms, ApplianceCatalog.appliances_for_room, ApplianceCatalog.wattage_for
- save_records, load_records
  - old: direct CSV functions
  - current: HouseholdRecordRepository.save_for_user and load_for_user
- compute_cost, build_record, get_total_cost, rank_by_room, rank_by_appliance, check_budget
  - old: procedural computation.py
  - current: EnergyComputationService, RankingService, BudgetService
- main loop orchestration
  - old: single main function
  - current: main.py + WattzUpApplicationService + WattzUpCLI/WattzUpVisual

## Fundamentals to Technicals

### Python foundations used
- Data structures:
  - dict for appliance catalogs and record dictionaries,
  - list for record collections and rankings,
  - tuple for ranked room outputs.
- Control flow:
  - if/elif for menu routing,
  - while loops for prompt-validation loops,
  - for loops for listing/aggregation.
- Functions and methods:
  - utility functions in adapters,
  - class methods and instance methods for OOP core.
- Classes:
  - dataclass for record model,
  - service/repository/catalog/application classes.
- Exceptions:
  - ValueError for invalid input,
  - RuntimeError for no active session,
  - KeyError for invalid room/appliance selections,
  - ModuleNotFoundError handling for GUI dependency fallback.
- File handling:
  - csv.DictWriter and csv.DictReader for persistence,
  - safe load behavior with malformed row skipping.

### OOP concepts used in this codebase
- Encapsulation:
  - persistence internals in HouseholdRecordRepository,
  - computation internals in services.
- Separation of concerns:
  - UI separate from domain logic,
  - orchestration separate from persistence and math.
- Orchestration:
  - WattzUpApplicationService is the coordinator between interface, services, and repository.
- Composition over inheritance:
  - Application service receives repository/catalog/services via constructor.

### CSV persistence fundamentals and why CSV is used
- CSV is human-readable and easy for class projects and demos.
- CSV maps naturally to flat appliance records.
- DictReader/DictWriter preserve named columns and readability.
- Current schema uses fixed field names in repository._FIELDNAMES.

## File-by-File Guide

### docs/TASK-OWNERSHIP.md
- Purpose: legacy ownership plan and functional contracts.
- Main content: role split (Data Layer, Computation, UI, Integration), required function names.
- Inputs/outputs: documentation-only.
- Side effects: none.
- Collaboration: used as legacy reference for mapping to current modules.

### main.py
- Purpose: entrypoint and runtime mode selection.
- Main functions: _build_parser, run_cli, run_gui, main.
- Inputs/outputs:
  - input: command flags (for example --cli),
  - output: starts GUI event loop or CLI loop.
- Side effects: launches UI, prints fallback message if GUI deps are missing.
- Collaboration: wires lib.app with lib.cli_app and lib.ui.

### lib/app.py
- Purpose: central application orchestration and session state.
- Main class/functions: WattzUpApplicationService, create_default_application_service.
- Inputs/outputs:
  - input: user/session actions (create/continue/add/save/load/rank/budget),
  - output: typed records, ranking lists, status strings.
- Side effects: mutates in-memory session records and writes/reads files through repository.
- Collaboration: uses lib.catalog, lib.services, lib.repository.

### lib/catalog.py
- Purpose: room/appliance metadata lookups.
- Main class: ApplianceCatalog.
- Inputs/outputs:
  - input: room, appliance,
  - output: room list, appliance list, wattage int.
- Side effects: none.
- Collaboration: reads util.config.APPLIANCE_LIBRARY.

### lib/models.py
- Purpose: canonical typed record model.
- Main class: ApplianceRecord dataclass.
- Inputs/outputs:
  - input: record fields,
  - output: to_dict/from_dict conversions.
- Side effects: none.
- Collaboration: used by services, app, repository, util adapters.

### lib/repository.py
- Purpose: per-user CSV persistence and validation.
- Main class: HouseholdRecordRepository.
- Inputs/outputs:
  - input: username and records,
  - output: saved CSV file or loaded list of ApplianceRecord.
- Side effects: filesystem read/write under data/.
- Collaboration: uses model + config constants.

### lib/services.py
- Purpose: business logic services.
- Main classes: EnergyComputationService, RankingService, BudgetService.
- Inputs/outputs:
  - input: records and numeric values,
  - output: computed records, totals, rankings, budget status.
- Side effects: none.
- Collaboration: called by app service and util/computation adapter.

### lib/cli_app.py
- Purpose: terminal interface implementation.
- Main class: WattzUpCLI.
- Inputs/outputs:
  - input: terminal prompts,
  - output: console display and app service calls.
- Side effects: user interaction loop, may trigger save/load through app service.
- Collaboration: calls WattzUpApplicationService and uses config usage options.

### lib/ui.py
- Purpose: GUI interface implementation using customtkinter.
- Main class: WattzUpVisual.
- Inputs/outputs:
  - input: dialogs/buttons,
  - output: GUI updates and app service calls.
- Side effects: window lifecycle, message dialogs, save/load through app service.
- Collaboration: calls WattzUpApplicationService and config usage options.

### util/config.py
- Purpose: centralized constants and static mappings.
- Main symbols: APPLIANCE_LIBRARY, USAGE_LEVELS, DEFAULT_RATE_PER_KWH, DATA_DIRECTORY, USER_RECORD_SUFFIX.
- Inputs/outputs: constants only.
- Side effects: none.
- Collaboration: imported by catalog, repository, services, UI/CLI.

### util/data_layer.py
- Purpose: backward-compatible procedural API adapter for data-layer functions.
- Main class/functions: DataLayerFacade, get_rooms/get_appliances/get_wattage/save_records/load_records.
- Inputs/outputs:
  - input: legacy function-style parameters,
  - output: same-style values as original contract.
- Side effects: file I/O through repository.
- Collaboration: bridges legacy function contracts to new class-based internals.

### util/computation.py
- Purpose: backward-compatible procedural API adapter for computation functions.
- Main class/functions: ComputationFacade plus compute_cost/build_record/get_total_cost/ranking/check_budget wrappers.
- Inputs/outputs:
  - input: legacy function-style parameters,
  - output: dict/list/tuple outputs matching old API shape.
- Side effects: none directly; pure computations.
- Collaboration: maps old contracts to services.

### README.md
- Purpose: project-level overview, run instructions, concepts, and technical summary.
- Inputs/outputs: documentation-only.
- Side effects: none.
- Collaboration: aligns external understanding with implementation.

## Class and Function Reference

### main.py

#### _build_parser() -> argparse.ArgumentParser
- Parameters: none.
- Returns: configured parser with --cli.
- Exceptions: none.
- Typical call site: main().

#### run_cli() -> None
- Parameters: none.
- Returns: none.
- Exceptions: propagates runtime exceptions from CLI loop if any.
- Typical call site: main() when --cli is set or GUI fallback.

#### run_gui() -> None
- Parameters: none.
- Returns: none.
- Exceptions:
  - raises RuntimeError when GUI modules are unavailable.
- Typical call site: main().

#### main() -> None
- Parameters: none.
- Returns: none.
- Exceptions: handles RuntimeError from run_gui and falls back to CLI.
- Typical call site: module entrypoint.

### lib.app.WattzUpApplicationService

#### __init__(repository, catalog, computation_service, ranking_service, budget_service) -> None
- Parameters:
  - repository: HouseholdRecordRepository,
  - catalog: ApplianceCatalog,
  - computation_service: EnergyComputationService,
  - ranking_service: RankingService,
  - budget_service: BudgetService.
- Returns: none.
- Side effects: initializes in-memory session state.

#### catalog (property) -> ApplianceCatalog
- Returns the catalog dependency.

#### list_existing_users() -> list[str]
- Returns usernames from repository.
- Typical call sites: CLI/GUI startup.

#### create_new_user_session(username: str) -> str
- Validates/sanitizes and initializes empty session.
- Raises ValueError for empty/invalid/duplicate usernames.
- Typical call sites: CLI _startup_flow, GUI _create_new_user.

#### continue_user_session(username: str) -> str
- Sanitizes username and loads records from repository.
- Raises ValueError for invalid username.
- Typical call sites: CLI _startup_flow, GUI _continue_existing_user.

#### add_appliance_usage(room: str, appliance: str, usage_level: str) -> ApplianceRecord
- Computes and appends new record, then auto-saves.
- Raises:
  - KeyError for unknown room/appliance pair,
  - ValueError for invalid usage level,
  - RuntimeError when no active session.
- Typical call sites: CLI _add_appliance_flow, GUI _add_entry.

#### save_current_session() -> None
- Persists current records for active user.
- Raises RuntimeError when no session exists.
- Typical call sites: CLI _save_records, GUI _save_data, app add_appliance_usage.

#### load_current_session() -> None
- Reloads current user records from disk.
- Raises RuntimeError when no session exists.
- Typical call sites: CLI _load_records.

#### clear_records() -> None
- Resets in-memory records to empty list.
- Typical call sites: CLI _clear_records.

#### set_budget(budget: float | None) -> None
- Sets budget; validates non-negative values.
- Raises ValueError if budget < 0.
- Typical call sites: CLI _set_budget, GUI _set_budget_ui.

#### total_cost() -> float
- Aggregates monthly_cost across in-memory records.
- Typical call sites: dashboard displays in GUI/CLI.

#### budget_status() -> str
- Returns NOT SET, UNDER BUDGET, or OVER BUDGET.
- Typical call sites: dashboard displays in GUI/CLI.

#### ranked_appliances() -> list[ApplianceRecord]
- Returns records sorted descending by monthly cost.
- Typical call sites: ranking screens in GUI/CLI.

#### ranked_rooms() -> list[tuple[str, float]]
- Returns room totals sorted descending.
- Typical call sites: ranking screens in GUI/CLI.

#### create_default_application_service() -> WattzUpApplicationService
- Factory that wires default repository, catalog, and services.
- Typical call sites: main.run_cli and main.run_gui.

### lib.catalog.ApplianceCatalog

#### __init__(appliance_library: dict[str, dict[str, int]] | None = None) -> None
- Optional custom catalog injection.

#### rooms() -> list[str]
- Returns room names.

#### appliances_for_room(room: str) -> list[str]
- Returns appliances for room; empty list for unknown room.

#### wattage_for(room: str, appliance: str) -> int
- Returns wattage for pair.
- Raises KeyError for unknown pair.

### lib.models.ApplianceRecord

#### dataclass fields
- room: str
- appliance: str
- wattage: int
- usage_level: str
- hours_per_day: int
- kwh: float
- monthly_cost: float

#### to_dict() -> dict[str, Any]
- Converts model instance into dictionary.

#### from_dict(data: dict[str, Any]) -> ApplianceRecord
- Builds model from dictionary values.
- Raises KeyError/ValueError/TypeError if required fields are missing or invalid.

### lib.repository.HouseholdRecordRepository

#### __init__(data_directory: str = DATA_DIRECTORY, file_suffix: str = USER_RECORD_SUFFIX) -> None
- Creates data directory if missing.

#### sanitize_username(username: str) -> str
- Converts to safe filename fragment.
- Removes unsupported chars and trims separators.

#### user_file_path(username: str) -> str
- Returns per-user CSV file path.

#### list_usernames() -> list[str]
- Scans data directory for files ending with suffix.
- Deduplicates case-insensitively.

#### username_exists(username: str) -> bool
- Case-insensitive existence check.

#### save_for_user(username: str, records: list[ApplianceRecord]) -> None
- Writes CSV header and rows.
- Side effect: overwrites existing user file.

#### load_for_user(username: str) -> list[ApplianceRecord]
- Reads CSV and returns valid rows only.
- Missing file returns empty list.

#### _row_to_record(row: dict[str, str]) -> ApplianceRecord | None
- Internal validator/parser.
- Returns None for malformed/invalid values.

### lib.services.EnergyComputationService

#### __init__(rate_per_kwh: float = DEFAULT_RATE_PER_KWH) -> None
- Stores rate used in calculations.

#### build_record(room: str, appliance: str, wattage: int, usage_level: str) -> ApplianceRecord
- Uses usage level map to derive hours/day.
- Computes kwh and monthly_cost.
- Raises ValueError for unknown usage level.

#### total_cost(records: list[ApplianceRecord]) -> float
- Sums monthly_cost values.

### lib.services.RankingService

#### rank_appliances(records: list[ApplianceRecord]) -> list[ApplianceRecord]
- Sorts descending by monthly_cost.

#### rank_rooms(records: list[ApplianceRecord]) -> list[tuple[str, float]]
- Aggregates by room then sorts descending.

### lib.services.BudgetService

#### budget_status(total_cost: float, budget: float | None) -> str
- Returns NOT SET if budget is None.
- Otherwise returns UNDER BUDGET or OVER BUDGET.

### lib.cli_app.WattzUpCLI (important methods)
- run() -> None: main CLI loop.
- _startup_flow() -> str: choose new vs existing user.
- _add_appliance_flow() -> None: room->appliance->usage->add.
- _set_budget() -> None: prompt and set numeric budget.
- _save_records()/_load_records() -> None: persistence actions.
- _prompt_autosave_on_exit() -> None: exit-save confirmation.

### lib.ui.WattzUpVisual (important methods)
- __init__(application_service: WattzUpApplicationService | None = None) -> None: builds GUI and starts login flow.
- _login_user() -> None: choose continue/new via dialogs.
- _show_map() -> None: dashboard summary and room hotspots.
- _fill_card_content(room_name, color) -> None: tabbed room detail panel.
- _add_entry(room, appliance, usage_level, color) -> None: add and refresh.
- _set_budget_ui() -> None: budget dialog.
- _save_data() -> None: save action with messagebox.
- _on_window_close() -> None: optional save before close.

### util.data_layer adapter functions
- get_rooms() -> list[str]
- get_appliances(room: str) -> list[str]
- get_wattage(room: str, appliance: str) -> int
- save_records(records: list[dict], filename: str = "data/household_records.csv") -> None
- load_records(filename: str = "data/household_records.csv") -> list[dict]

### util.computation adapter functions
- compute_cost(wattage: int, hours_per_day: int, rate: float = 12.0) -> dict
- build_record(room, appliance, wattage, usage_level, hours_per_day, rate=12.0) -> dict
- get_total_cost(records: list[dict]) -> float
- rank_by_room(records: list[dict]) -> list[tuple[str, float]]
- rank_by_appliance(records: list[dict]) -> list[dict]
- check_budget(total_cost: float, budget: float | None) -> str

## End-to-End Flow Walkthroughs

### Startup flow: python main.py and mode selection
1. main.main parses args.
2. If --cli is present, it calls run_cli.
3. Otherwise it tries run_gui.
4. If GUI modules are missing, RuntimeError is handled and CLI fallback starts.

### New/continue user session flow
1. Interface asks whether to create new or continue existing user.
2. Interface calls application service:
   - create_new_user_session(username), or
   - continue_user_session(username).
3. Application service sanitizes username through repository logic.
4. Continue flow loads records from data/<username>_household_records.csv.

### Add appliance flow (room -> appliance -> usage -> computation -> save)
1. Interface collects room and appliance selections from catalog.
2. Interface collects usage level (Heavy, Moderate, Eco).
3. Interface calls add_appliance_usage(room, appliance, usage_level).
4. Application service fetches wattage from ApplianceCatalog.
5. EnergyComputationService builds ApplianceRecord with computed kwh and monthly_cost.
6. Record is appended in memory.
7. Application service auto-saves entire session via repository.save_for_user.
8. Interface refreshes dashboard/ranking views.

### Ranking flow (appliance + room)
1. Interface requests ranking view.
2. App service delegates to RankingService:
   - ranked_appliances returns sorted record list.
   - ranked_rooms returns grouped room totals.
3. Interface renders ranking output.

### Budget flow
1. Interface prompts budget input.
2. App service validates and stores budget.
3. Dashboard requests total_cost and budget_status.
4. BudgetService returns NOT SET, UNDER BUDGET, or OVER BUDGET.

### Save/load flow
- Save:
  1. Interface calls save_current_session.
  2. Repository writes CSV header plus all record rows.
- Load:
  1. Interface calls load_current_session.
  2. Repository parses CSV and skips invalid rows.
  3. App state records list is replaced with loaded valid rows.

## Error Handling Deep Dive

### Validation and error handling by layer

| Layer | Validation or error handling |
|---|---|
| UI (CLI/GUI) | validates prompt choices and numeric parsing loops; catches exceptions from app service to show friendly messages |
| Application service | validates active session, budget non-negative, username validity and uniqueness |
| Services | validates usage_level in computation |
| Repository | sanitizes usernames, handles missing files by returning empty list, skips malformed/invalid CSV rows |
| Launcher main.py | handles missing GUI dependencies and falls back to CLI |

### Common failure scenarios and where handled
| Scenario | Handling location | Behavior |
|---|---|---|
| Non-numeric menu choice (CLI) | lib/cli_app.py prompt loops | re-prompt user |
| Invalid budget input | lib/cli_app.py and lib/ui.py | show error and keep previous budget |
| Duplicate username | lib/app.py create_new_user_session | raises ValueError; UI reports message |
| Invalid room/appliance pair | lib/catalog.py wattage_for | raises KeyError; UI/CLI catches and reports |
| No active session but save/load called | lib/app.py | raises RuntimeError; UI/CLI shows message |
| Corrupted CSV rows | lib/repository.py _row_to_record | row skipped silently |
| Missing user file | lib/repository.py load_for_user | returns empty list |
| Missing GUI deps | main.py run_gui/main | prints message and runs CLI fallback |

### User-visible behavior in GUI/CLI
- GUI uses messagebox dialogs for errors and confirmations.
- CLI prints clear text errors and loops until valid input.
- Both interfaces maintain continuity without crashing on common bad input.

## Data Contract and Persistence Format

### Canonical record fields
| Field | Type | Meaning |
|---|---|---|
| room | str | room category (Kitchen, Bedroom, etc.) |
| appliance | str | selected appliance name |
| wattage | int | power draw in watts |
| usage_level | str | Heavy, Moderate, Eco |
| hours_per_day | int | mapped from usage level |
| kwh | float | monthly energy estimate |
| monthly_cost | float | monthly peso estimate |

### CSV columns and data types
CSV columns are fixed and ordered:
- room (str)
- appliance (str)
- wattage (int)
- usage_level (str)
- hours_per_day (int)
- kwh (float)
- monthly_cost (float)

### Record lifecycle from input to disk and back
1. User chooses room, appliance, usage level.
2. Catalog resolves wattage.
3. Computation service calculates kwh and monthly cost and builds ApplianceRecord.
4. App service appends the record and triggers save.
5. Repository serializes record fields to CSV.
6. On load, repository parses each row and validates values.
7. Valid rows become ApplianceRecord objects and replace current in-memory list.

## Developer Ownership Guide

### Data Layer ownership focus
- Master first:
  - util/config.py constants,
  - lib/catalog.py lookups,
  - lib/repository.py persistence.
- Be ready to explain:
  - sanitize_username,
  - save_for_user/load_for_user,
  - _row_to_record validation rules.
- Common mistakes:
  - changing CSV column names without updating _FIELDNAMES,
  - mismatched file suffix assumptions,
  - forgetting case-insensitive username uniqueness.
- Debug tips:
  - print resolved file path from user_file_path,
  - inspect CSV headers and row types.

### Computation ownership focus
- Master first:
  - lib/services.py math and ranking methods,
  - util/computation.py adapter behavior.
- Be ready to explain:
  - build_record formula,
  - room aggregation logic,
  - budget status decision.
- Common mistakes:
  - inconsistent rounding,
  - mixing NOT SET with legacy No budget set wording.
- Debug tips:
  - create 2-3 known records and verify totals manually.

### UI ownership focus
- Master first:
  - lib/cli_app.py startup loop and add flow,
  - lib/ui.py login/card/budget/save interactions.
- Be ready to explain:
  - how both interfaces call the same app service,
  - where input validation loops happen.
- Common mistakes:
  - bypassing app service and mutating records directly,
  - unhandled exceptions from app service calls.
- Debug tips:
  - test create/continue user paths separately,
  - test cancel actions in GUI dialogs.

### Integration ownership focus
- Master first:
  - main.py mode selection and fallback,
  - lib/app.py orchestration methods.
- Be ready to explain:
  - dependency wiring in create_default_application_service,
  - end-to-end add/save/load flow.
- Common mistakes:
  - inconsistent session assumptions,
  - forgetting autosave behavior expectations.
- Debug tips:
  - run both python main.py and python main.py --cli,
  - verify data directory outputs after each save.

## Testing and Verification Checklist

### Basic startup and mode checks
- Run python main.py.
- If GUI dependencies are missing, verify CLI fallback message appears.
- Run python main.py --cli and verify CLI starts directly.

### Session and user checks
- Create a new unique username and verify file is created after first add/save.
- Try duplicate username with different letter case and verify rejection.
- Continue existing user and verify records load.

### Add flow and computations
- Add one Kitchen Rice Cooker Moderate entry and verify monthly cost is 576.00 at rate 12.0.
- Add multiple entries and verify total cost equals sum of entry costs.

### Ranking checks
- Verify appliance ranking is descending by monthly_cost.
- Verify room ranking aggregates all room entries correctly.

### Budget checks
- Set budget below total and verify OVER BUDGET.
- Set budget above total and verify UNDER BUDGET.
- Leave budget unset and verify NOT SET behavior.

### Persistence and malformed data checks
- Save records, restart, and load to confirm persistence.
- Manually edit CSV with one malformed row (missing column or invalid number).
- Reload and verify malformed row is skipped while valid rows still load.

### Negative and invalid input checks
- Enter non-numeric values in CLI numeric prompts and verify re-prompt.
- Try negative budget and verify validation handling.
- Attempt add with invalid usage level via adapter tests and verify ValueError.

## Quick Recitation Script (Short)

### Member 1 Data Layer script (about 60-90 seconds)
My part is the data foundation. The appliance list and usage presets are in util/config.py. The room and appliance access API is in lib/catalog.py. File persistence is in lib/repository.py, where each user has a CSV file in data/. I sanitize usernames, write records with CSV headers, and load records while skipping malformed rows. The key idea is safe persistence with predictable data contracts.

### Member 2 Computation script (about 60-90 seconds)
My part is the computation and analysis logic in lib/services.py. EnergyComputationService turns wattage and usage level into kwh and monthly_cost using the formula wattage times hours times 30 over 1000, then multiplies by rate. RankingService sorts appliances and aggregates room totals. BudgetService returns NOT SET, UNDER BUDGET, or OVER BUDGET. These services are pure logic and easy to test.

### Member 3 UI script (about 60-90 seconds)
My part is user interaction. The CLI is in lib/cli_app.py and the GUI is in lib/ui.py. Both collect input and display output, but they do not do business logic directly. They call the shared application service in lib/app.py. This keeps behavior consistent between GUI and CLI and makes the interface code focused on prompts, validation loops, and display.

### Member 4 Integration script (about 60-90 seconds)
My part is integration and startup. main.py is the single entrypoint. It launches GUI by default and supports --cli for terminal mode, with fallback to CLI if GUI dependencies are missing. In lib/app.py, WattzUpApplicationService manages session state and orchestrates catalog, computation services, and repository. The add flow computes a record and auto-saves, so the app keeps data consistent.

## Where to Extend Next
1. Add automated unit tests for repository validation and all service methods.
2. Add import/export tools for historical monthly reports.
3. Add configurable electricity rate through UI and persisted user preferences.
4. Add richer analytics (trend chart, highest-cost appliance over time).
5. Add stronger logging and optional warning output for skipped malformed CSV rows.
