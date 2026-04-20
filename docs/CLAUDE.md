# CLAUDE.md

## Optimized Prompt for Claude

Use this prompt in Claude to regenerate documentation that accurately reflects the refactored, mainly object-oriented codebase.

```text
You are a senior technical writer and documentation editor.

Repository context:
- Project: WattzUp: Electricity Consumption Monitoring System
- Stack: Python
- Architecture status: Refactored to mainly object-oriented design.
- Runtime behavior: GUI is default (`python main.py`), CLI is optional (`python main.py --cli`).
- Key files include: `main.py`, `lib/ui.py`, `lib/cli_app.py`, `lib/app.py`, `lib/services.py`, `lib/repository.py`, `lib/models.py`, `lib/catalog.py`, and `util/config.py`.
- Current dashboard modules include room donut visualization, insights cards, and a searchable records table.
- GUI dependencies include `customtkinter`, `Pillow`, and `matplotlib`.

Your tasks:
1) Recreate `README.md` with improved voice and tone.
2) Create a slides-ready version of the same content.

Primary writing requirements:
- Voice and tone must be simple, straightforward, descriptive, and thorough.
- Keep language concrete and plain; avoid hype and filler.
- Ensure all architecture statements match the current OOP implementation.
- Do not describe the app as primarily procedural.

Execution instructions:
- Read current `README.md` and relevant source files before writing.
- Preserve factual identity (title, members, purpose), while improving clarity and structure.
- Explicitly document OOP layers and class responsibilities.
- Ensure commands and runtime behavior are correct and testable.

Deliverables:
A) Replace `README.md` with a production-quality version including:
- Project Title
- Group Members
- Brief Description of the System
- Objectives of the Project
- Features and Functionalities
- Programming Concepts Applied (OOP|Functional|Procedural)
- Explanation of File Handling Used
- Explanation of Error Handling Implemented
- Instructions on How to Run the Program

B) Create `docs/README_SLIDES.md` as a slides-ready version:
- 1 slide per top-level heading
- Bullets only (no paragraphs)
- Max 6 bullets per slide
- Max 12 words per bullet
- Include opening and closing slides
- Include one "Demo Flow" slide with usage steps

Quality checks before final output:
- No contradiction with code behavior or architecture.
- OOP-first architecture is clearly and accurately documented.
- Commands are runnable as written.
- Wording is consistent, grammar is clean, and structure is logical.

Output format:
1. Summary of documentation changes
2. Updated `README.md`
3. New `docs/README_SLIDES.md`
4. Brief rationale for wording/structure decisions
```

## Notes

- Re-run this prompt whenever code behavior or architecture changes.
- Prioritize accuracy and clarity over verbosity.
