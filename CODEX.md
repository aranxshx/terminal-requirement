# CODEX.md

## Optimized Prompt for Codex 5.3

Use the following prompt with `gpt-5.3-codex` to generate `EXPLANATION.md`.

```text
You are a senior software engineer and technical educator.

Your task: create `EXPLANATION.md` for this repository as a comprehensive developer guide.

Primary objective:
Produce a clear, thorough explanation of the system from fundamentals to implementation details, explicitly aligned with `docs/TASK-OWNERSHIP.md`, while accurately reflecting the CURRENT refactored codebase.

Critical requirements:
1) Read first before writing:
- `docs/TASK-OWNERSHIP.md`
- `main.py`
- `lib/app.py`
- `lib/catalog.py`
- `lib/models.py`
- `lib/repository.py`
- `lib/services.py`
- `lib/cli_app.py`
- `lib/ui.py`
- `util/config.py`
- `util/data_layer.py`
- `util/computation.py`
- `README.md`

2) Then create `EXPLANATION.md` that includes ALL of the following sections:

- Project Orientation
  - What the app does
  - Why it exists
  - High-level architecture in plain English

- Architecture Overview
  - Layered diagram (interface -> application -> domain services -> repository/model -> config)
  - Responsibilities and boundaries per layer
  - Why this separation matters

- Task Ownership Mapping (Legacy -> Current)
  - Map each part in `docs/TASK-OWNERSHIP.md` to current modules/classes/functions
  - Explicitly call out renamed, moved, or refactored items
  - Example: old function-style responsibilities vs current class/service methods

- Fundamentals to Technicals
  - Python foundations used (data structures, control flow, functions, classes, exceptions, file handling)
  - OOP concepts used in this codebase (encapsulation, separation of concerns, orchestration)
  - CSV persistence fundamentals and why `.csv` is used

- File-by-File Guide
  - For each listed file, explain:
    - Purpose
    - Main classes/functions
    - Inputs/outputs
    - Side effects (file I/O, state changes)
    - How it collaborates with other modules

- Class and Function Reference
  - For every important class and function/method, include:
    - Signature
    - Parameter meanings
    - Return value
    - Error/exception behavior
    - Typical call sites in the project

- End-to-End Flow Walkthroughs
  - Startup flow (`python main.py`) and mode selection (`--cli`)
  - New/continue user session flow
  - Add appliance flow (room -> appliance -> usage -> computation -> save)
  - Ranking flow (appliance + room)
  - Budget flow
  - Save/load flow

- Error Handling Deep Dive
  - Validation and error handling by layer (UI, app service, repository)
  - Common failure scenarios and where they are handled
  - User-visible behavior in GUI/CLI for each scenario

- Data Contract and Persistence Format
  - Canonical record fields and meaning
  - CSV columns and data types
  - Record lifecycle from input to disk and back

- Developer Ownership Guide
  - Section per ownership area (Data Layer, Computation, UI, Integration)
  - For each area:
    - What to master first
    - Which files to focus on
    - Which functions/classes to be able to explain in recitation/demo
    - Common mistakes and debugging tips

- Testing and Verification Checklist
  - Practical checklist developers can run manually
  - Include edge cases for bad input and corrupted CSV rows

- Quick Recitation Script (Short)
  - 60-90 second summary each member can use to explain their part

3) Accuracy constraints:
- Do NOT invent files/functions.
- If `TASK-OWNERSHIP` references old files (e.g., single-file merge plans), clearly mark as legacy and provide current equivalent.
- Keep examples consistent with current code behavior.

4) Writing style constraints:
- Simple, straightforward, descriptive, thorough.
- No fluff, no hype.
- Use headings, concise paragraphs, and readable tables where helpful.
- Prioritize clarity for student developers preparing to explain code.

5) Deliverable format:
- Write to `EXPLANATION.md`.
- Start with a short "How to use this guide" section.
- End with a "Where to extend next" section.

6) Final output to user (after creating file):
- Summary of what was documented
- Any legacy-to-current mismatches discovered
- List of files analyzed
```

## Notes

- This prompt is designed for your current refactored layout (`main.py`, `lib/`, `util/`).
- Re-run this prompt whenever architecture or file layout changes.
