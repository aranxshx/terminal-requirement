Got it. Here's the slide-by-slide content spec for `docs/README_SLIDES.md`:

---

# WattzUp â€” Slides Content Spec
`docs/README_SLIDES.md`

---

## Slide 1 â€” Title (Opening)
- **Title:** WattzUp: Electricity Consumption Monitoring System
- **Subtitle:** A Python-based household energy tracker
- **Group Members:** Kyle Yuan L. Uy Â· Jefferson S. Magoliman Â· Andrew P. Eroyla Â· Wilbert F. Mijares

---

## Slide 2 â€” What is WattzUp?
- Tracks household appliance electricity usage
- Computes monthly kWh consumption and estimated cost
- Supports multiple users with separate record files
- Includes dashboard analytics (room donut, insights, full records table)
- GUI-first; CLI available as fallback
- No external APIs or smart-meter hardware required

---

## Slide 3 â€” Objectives
- Build a practical electricity monitoring tool for households
- Compute monthly energy use from wattage and usage level
- Organize records per user with persistent storage
- Apply object-oriented design with clear separation of concerns
- Provide usable interfaces across GUI and CLI

---

## Slide 4 â€” System Architecture
- Layered OOP design: interface â†’ service â†’ repository â†’ model
- `lib/app.py` â€” `WattzUpApplicationService` coordinates all session state
- `lib/services.py` â€” domain services for computation, ranking, and budget
- `lib/repository.py` â€” CSV persistence, loading, and validation
- `lib/models.py` â€” shared `ApplianceRecord` data model
- `lib/ui.py` / `lib/cli_app.py` â€” thin interface layers over the same backend

---

## Slide 5 â€” Programming Concepts Applied
- **Object-Oriented (primary):** encapsulated classes for each domain concern
- **Functional (supporting):** sorting, aggregation, and transformation helpers
- **Procedural (interface only):** menu and interaction loops in CLI/GUI layers
- OOP ensures consistent behavior across both interfaces
- Clear boundaries between logic, persistence, and presentation

---

## Slide 6 â€” Features and Functionalities
- Create or continue a per-user session at startup
- Add appliance entries by room with wattage and usage level
- Automatic kWh and monthly cost computation on entry
- Dashboard donut chart for room cost share and totals
- Dashboard insights with budget/cost/usage focus filter
- Full records table with search, filter, and sort controls

---

## Slide 7 â€” How the Computation Works
- Formula: `kWh = (wattage Ã— hours/day Ã— 30) / 1000`
- Monthly cost: `kWh Ã— rate per kWh`
- Default rate: **â‚±12.00 / kWh** (configurable in `util/config.py`)
- Usage presets: Heavy = 8 hrs Â· Moderate = 4 hrs Â· Eco = 1 hr
- Computation triggered automatically on each new entry

---

## Slide 8 â€” File Handling
- Records stored in `data/<username>_household_records.csv`
- One file per user; usernames are case-insensitively validated
- Files written in CSV format with typed, headered rows
- Malformed or incomplete rows are skipped on load â€” no crashes
- Username sanitization applied before file path resolution

---

## Slide 9 â€” Error Handling
- Invalid menu/input values are rejected and re-prompted
- Unknown usage levels raise validation errors in service layer
- Invalid usernames are blocked before session creation/continuation
- Missing user session blocks save/load with clear runtime messages
- Malformed CSV rows are skipped safely during load
- GUI startup falls back to CLI if GUI dependencies are missing

---

## Slide 10 â€” Demo Flow
1. Run `python main.py` to launch the GUI
2. Create a new user or continue an existing one
3. Add appliances by room, wattage, and usage level
4. Review donut chart, insights, and records table updates
5. Set a monthly budget and verify insight changes
6. Save session; autosave prompt shown on exit

---

## Slide 11 â€” How to Run
- **GUI (default):** `python main.py`
- **CLI (fallback):** `python main.py --cli`
- GUI requires `customtkinter`, `Pillow`, and `matplotlib`
- Single gateway: `main.py` is the only launcher
- All data files auto-created in `data/` on first save

---

## Slide 12 â€” Closing
- **Title:** WattzUp
- **Tagline:** Simple tracking. Smarter household energy habits.
- Group Members: Kyle Yuan L. Uy Â· Jefferson S. Magoliman Â· Andrew P. Eroyla Â· Wilbert F. Mijares

---

12 slides total. Each maps to one top-level section of the README with bullets trimmed to â‰¤12 words each and â‰¤6 bullets per slide. The Demo Flow slide on slide 10 uses numbered steps as specified.

