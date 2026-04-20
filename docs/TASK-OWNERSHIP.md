# TASK OWNERSHIP PLAN â€” WattzUp
### Programming Languages Terminal Requirement | Sunfall Studios

---

## Parallel-First Team Rules

To avoid blocking each other, follow these ground rules from Day 1:

- **Agree on a shared data contract early** (see Appendix below) â€” a standard Python dictionary/list structure that all members reference.
- **Each member develops with stub/sample data first**, then switches to the real integrated data.
- **Never wait for another member's code** â€” use a placeholder function if needed and replace it during integration.
- **Short checkpoints** (not one big merge at the end) keep everyone aligned.

---

## Part 1 â€” Data Layer: Appliance Library & Record Storage
**Owner: Member 1**

### What You Own
You are responsible for the **foundation data** of the entire system. This includes:
- Defining the master appliance dictionary (rooms â†’ appliances â†’ wattage)
- Defining usage level mappings (Heavy, Moderate, Eco â†’ hours/day)
- Writing `save_records()` and `load_records()` functions for `household_records.csv`
- Writing a helper to parse and validate lines read from file

### Specific Tasks
1. Create the `APPLIANCE_LIBRARY` dictionary structured as:
   ```python
   APPLIANCE_LIBRARY = {
       "Kitchen": {
           "Rice Cooker": 400,
           "Electric Kettle": 1500,
           # ... etc.
       },
       # ... other rooms
   }
   ```
2. Create the `USAGE_LEVELS` dictionary:
   ```python
   USAGE_LEVELS = {
       "Heavy": 8,
       "Moderate": 4,
       "Eco": 1
   }
   ```
3. Write `save_records(records, filename)`:
   - Accepts a list of record dicts
   - Writes each record as a CSV line to `household_records.csv`
4. Write `load_records(filename)`:
   - Reads `household_records.csv`
   - Returns a list of record dicts
   - Skips corrupted/incomplete lines silently
5. Write `get_rooms()` â€” returns list of available room names
6. Write `get_appliances(room)` â€” returns list of appliances for a given room
7. Write `get_wattage(room, appliance)` â€” returns the wattage integer

### Deliverables
- `data_layer.py` â€” contains all of the above (to be merged into `wattzup.py`)
- A sample `household_records.csv` with at least 5 dummy records (for testing)
- A short comment block at the top of your file explaining the data structure

### Dependencies
- **Depends on:** Nothing â€” you can start immediately
- **Blocks:** No one is blocked by you; others use stub data until you're done

### Notes
- The record dict format agreed upon by the team is:
  ```python
  {
      "room": "Kitchen",
      "appliance": "Rice Cooker",
      "wattage": 400,
      "usage_level": "Moderate",
      "hours_per_day": 4,
      "kwh": 48.0,
      "monthly_cost": 576.0
  }
  ```
- Do NOT write print statements inside your functions â€” return values instead. Let other members handle display.

---

## Part 2 â€” Computation Engine: Cost Calculation & Rankings
**Owner: Member 2**

### What You Own
You are responsible for all **math and analysis logic** â€” the brain of the system. You compute costs, rank rooms, rank appliances, and summarize totals.

### Specific Tasks
1. Write `compute_cost(wattage, hours_per_day, rate=12.0)`:
   - Formula: `kWh = (wattage * hours_per_day * 30) / 1000`
   - Formula: `cost = kWh * rate`
   - Returns a dict: `{"kwh": ..., "monthly_cost": ...}`
2. Write `build_record(room, appliance, wattage, usage_level, hours_per_day)`:
   - Uses `compute_cost()` internally
   - Returns the full record dict (as defined in the shared contract)
3. Write `get_total_cost(records)`:
   - Accepts the full list of records
   - Returns total monthly cost as a float
4. Write `rank_by_room(records)`:
   - Groups records by room, sums `monthly_cost` per room
   - Returns a sorted list of `(room, total_cost)` tuples, highest first
5. Write `rank_by_appliance(records)`:
   - Sorts all records by `monthly_cost`, highest first
   - Returns sorted list of record dicts
6. Write `check_budget(total_cost, budget)`:
   - Returns `"UNDER BUDGET"` or `"OVER BUDGET"` as string
   - Returns `"No budget set"` if budget is `None`

### Deliverables
- `computation.py` â€” contains all of the above (to be merged into `wattzup.py`)
- Use the shared stub record list below for development:
  ```python
  STUB_RECORDS = [
      {"room": "Kitchen", "appliance": "Rice Cooker", "wattage": 400, "usage_level": "Moderate", "hours_per_day": 4, "kwh": 48.0, "monthly_cost": 576.0},
      {"room": "Living Room", "appliance": "Aircon", "wattage": 1500, "usage_level": "Heavy", "hours_per_day": 8, "kwh": 360.0, "monthly_cost": 4320.0},
  ]
  ```

### Dependencies
- **Depends on:** Shared data contract only â€” you can start immediately with stubs
- **Blocks:** Member 3 (visualization) and Member 4 (dashboard display) need your functions â€” but both can mock them during development

### Notes
- All functions must **return values**, not print them.
- Use `round(value, 2)` for all cost outputs.
- Default rate is `â‚±12.00/kWh` â€” make it a parameter with a default value so it can be changed.

---

## Part 3 â€” User Interface: Menus, Display & Navigation
**Owner: Member 3**

### What You Own
You are responsible for **everything the user sees and interacts with** â€” menus, prompts, formatted output, and the dashboard display. You are the face of the system.

### Specific Tasks
1. Write `display_dashboard(records, budget)`:
   - Shows the main dashboard header
   - Shows estimated monthly cost
   - Shows budget status
   - Lists the main menu options `[1]â€“[6]` and `[0] Exit`
2. Write `display_room_menu(rooms)`:
   - Shows numbered list of rooms
   - Returns the user's valid selection (room name string)
3. Write `display_appliance_menu(appliances)`:
   - Shows numbered list of appliances for the selected room
   - Returns the user's valid appliance selection
4. Write `display_usage_menu()`:
   - Shows Heavy / Moderate / Eco options
   - Returns the selected usage level string
5. Write `display_room_ranking(ranked_rooms)`:
   - Shows rooms ranked by monthly cost, formatted and numbered
6. Write `display_appliance_ranking(ranked_appliances)`:
   - Shows appliances ranked by monthly cost, formatted and numbered
7. Write `prompt_budget()`:
   - Prompts the user to enter a monthly budget in pesos
   - Returns the float value

### Deliverables
- `ui.py` â€” contains all of the above (to be merged into `wattzup.py`)

### Dependencies
- **Depends on:** Shared data contract only â€” you can start immediately with stub data
- **Blocks:** Member 4 (main loop) needs your display functions, but Member 4 can use placeholder `print()` calls until you're ready

### Notes
- You do NOT handle the main `while True` loop â€” that's Member 4's job.
- You do NOT do math â€” that's Member 2's job.
- You do NOT read/write files â€” that's Member 1's job.
- Every display function should be **callable independently** for easy testing.
- Format monetary values as: `â‚±{value:,.2f}` (e.g., `â‚±4,320.00`)

### Sample Display Format to Follow
```
=========================================
         WATTZUP â€” DASHBOARD
=========================================
  Estimated Monthly Cost : â‚±5,476.00
  Budget Status          : OVER BUDGET âœ—

  [1] Manage Household
  [2] View Appliance Usage Ranking
  [3] View Room Usage Ranking
  [4] Set Monthly Budget
  [5] Save Records
  [6] Load Records
  [0] Exit
=========================================
```

---

## Part 4 â€” Main Loop, Error Handling & Integration
**Owner: Member 4**

### What You Own
You are the **integrator and quality gatekeeper**. You write the main program loop that ties everything together, implement all error handling, and prepare the final submission package.

### Specific Tasks
1. Write the **main program entry point** (`main()` function in `wattzup.py`):
   - Initialize records list and budget variable
   - Call `load_records()` on startup if file exists
   - Run the main `while True` menu loop
   - Route user selections to the correct Member 2 / Member 3 functions
2. Implement **all error handling** throughout the main loop:
   - Wrap all `input()` calls in `try/except` for non-numeric inputs
   - Catch `FileNotFoundError` when loading records
   - Catch corrupted/malformed file lines
   - Handle empty records list gracefully (show "No records yet" messages)
   - Validate all menu selections are within valid range
3. Write the **"add appliance" flow** connecting all modules:
   - Get room â†’ get appliance â†’ get usage level â†’ compute cost â†’ append to records list
4. Write `clear_records()` â€” resets the records list (with confirmation prompt)
5. Write the **auto-save prompt on exit** â€” ask user if they want to save before quitting
6. Assemble the **final `wattzup.py`** by merging all modules into one file
7. Prepare the **documentation file** (`documentation.txt`) for submission

### Deliverables
- `main_loop.py` â€” your portion before final merge (to be merged into `wattzup.py`)
- Final merged `wattzup.py` â€” the complete, single-file submission
- `documentation.txt` â€” the project documentation
- A quick **integration checklist** (see below)

### Dependencies
- **Depends on:** All other members' functions for final assembly
- **Early work:** You can stub all function calls (`compute_cost = lambda *a: {"kwh": 0, "monthly_cost": 0}`) and develop the loop skeleton immediately
- **Blocks:** Final submission â€” you produce the final file

### Integration Checklist (use before final submission)
```
[ ] APPLIANCE_LIBRARY covers all 5 rooms and all appliances
[ ] save_records() writes correctly to household_records.csv
[ ] load_records() reads back correctly and skips bad lines
[ ] compute_cost() returns correct values for all 3 usage levels
[ ] rank_by_room() and rank_by_appliance() return sorted results
[ ] dashboard displays correctly with no records (empty state)
[ ] dashboard displays correctly with records loaded
[ ] All menus reject invalid input without crashing
[ ] Budget comparison shows correctly when budget is and isn't set
[ ] Program exits cleanly with save prompt
[ ] household_records.csv sample file included in submission
[ ] documentation.txt is complete
```

### Error Handling Map (your responsibility)
| Scenario | How to Handle |
|---|---|
| Non-numeric menu input | `try/except ValueError` â€” re-prompt |
| Out-of-range menu choice | `if choice not in valid_range` â€” re-prompt |
| `household_records.csv` not found | `except FileNotFoundError` â€” print notice, continue |
| Corrupted line in file | `try/except` per line in `load_records()` â€” skip and warn |
| No appliances added yet | Check `if not records` â€” display empty state message |
| Budget not set | Pass `None` as budget â€” Member 2's `check_budget()` handles it |

---

## Minimal Blocking Dependency Map

```
Day 1 â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
         Member 1: Define APPLIANCE_LIBRARY, USAGE_LEVELS, stubs
         Member 2: Write compute/ranking functions (use stub records)
         Member 3: Write all display/menu functions (use stub data)
         Member 4: Write main loop skeleton (use lambda stubs)

Checkpoint A (mid-development): agree function names/signatures are stable
         Member 1: save_records() and load_records() are ready
         Member 2: All compute + ranking functions finalized
         Member 3: All display functions finalized
         Member 4: Connect real functions into loop, remove stubs

Checkpoint B (near deadline): full dry run
         Member 4: Merge all files into wattzup.py
         Member 4: Run through integration checklist
         All: Test together, fix any issues

Final â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
         Member 4 submits: wattzup.py, household_records.csv, documentation.txt, slides
```

---

## Appendix â€” Shared Data Contract

All members must use this exact structure for record dicts:

```python
record = {
    "room":         str,    # e.g., "Kitchen"
    "appliance":    str,    # e.g., "Rice Cooker"
    "wattage":      int,    # e.g., 400
    "usage_level":  str,    # "Heavy", "Moderate", or "Eco"
    "hours_per_day": int,   # 8, 4, or 1
    "kwh":          float,  # computed: (wattage * hours * 30) / 1000
    "monthly_cost": float   # computed: kwh * rate
}
```

File format for `household_records.csv` (CSV, one appliance per line):
```
room,appliance,wattage,usage_level,hours_per_day,kwh,monthly_cost
Kitchen,Rice Cooker,400,Moderate,4,48.0,576.0
Living Room,Aircon,1500,Heavy,8,360.0,4320.0
```

Function name contract (do NOT rename these):
| Function | Owner | Returns |
|---|---|---|
| `get_rooms()` | Member 1 | list of str |
| `get_appliances(room)` | Member 1 | list of str |
| `get_wattage(room, appliance)` | Member 1 | int |
| `save_records(records, filename)` | Member 1 | None |
| `load_records(filename)` | Member 1 | list of dicts |
| `compute_cost(wattage, hours, rate)` | Member 2 | dict |
| `build_record(room, appliance, wattage, usage_level, hours)` | Member 2 | dict |
| `get_total_cost(records)` | Member 2 | float |
| `rank_by_room(records)` | Member 2 | list of tuples |
| `rank_by_appliance(records)` | Member 2 | list of dicts |
| `check_budget(total_cost, budget)` | Member 2 | str |
| `display_dashboard(records, budget)` | Member 3 | None |
| `display_room_menu(rooms)` | Member 3 | str |
| `display_appliance_menu(appliances)` | Member 3 | str |
| `display_usage_menu()` | Member 3 | str |
| `display_room_ranking(ranked_rooms)` | Member 3 | None |
| `display_appliance_ranking(ranked_appliances)` | Member 3 | None |
| `prompt_budget()` | Member 3 | float |
| `main()` | Member 4 | None |
| `clear_records()` | Member 4 | list (empty) |

