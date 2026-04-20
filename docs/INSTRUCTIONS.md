# WattzUp: Electricity Consumption Monitoring System
### Programming Languages â€” Terminal Requirement | Sunfall Studios

---

## Activity Overview

Build a **Python terminal system** that helps users record, monitor, and calculate household electricity consumption.

Your program must:
- Allow users to manage rooms and appliances in a household
- Accept usage level inputs per appliance
- Compute estimated electricity costs based on wattage and usage
- Rank rooms and appliances by consumption
- Save and load household records using file handling
- Display a clean dashboard with monthly cost estimates

---

## Learning Objectives
- Apply **file handling** by saving and loading household records to/from a file
- Use **functions** to organize appliance logic, cost computation, and display
- Use **lists and dictionaries** to store rooms, appliances, and usage data
- Apply **control structures** (`if`, `elif`, `else`, `for`, `while`) for menu navigation and validation
- Use **data types** (int, float, string, bool) appropriately throughout the system
- Demonstrate **error handling** for invalid inputs and missing files
- Practice clean, readable, and modular Python code

---

## System Idea

The user acts as the **manager of a household** and can:
1. Select a room or area in their home
2. Choose appliances per room
3. Set estimated usage level (Heavy, Moderate, Eco)
4. View total electricity consumption and estimated monthly cost
5. Track which room and appliance consumes the most electricity
6. Save and load household records

---

## Program Flow

### Main Dashboard
```
=========================================
       WATTZUP â€” DASHBOARD
=========================================
  Estimated Monthly Cost: P[cost]
  Budget Status: [Under / Over Budget]

  [1] Manage Household
  [2] View Appliance Usage Ranking
  [3] View Room Usage Ranking
  [4] Set Monthly Budget
  [5] Save Records
  [6] Load Records
  [0] Exit
=========================================
```

### Room Selection
```
SELECT ROOM:
  [1] Bathroom
  [2] Kitchen
  [3] Dining Area
  [4] Living Room
  [5] Bedroom
  [0] Back
```

### Appliance Selection (per room)
Each room has a fixed set of appliances with predefined wattage values:

| Room         | Appliance       | Wattage (W) |
|--------------|-----------------|-------------|
| Bathroom     | Lights          | 15          |
| Bathroom     | Hair Dryer      | 1200        |
| Bathroom     | Charger         | 10          |
| Bathroom     | Water Heater    | 2000        |
| Kitchen      | Rice Cooker     | 400         |
| Kitchen      | Electric Kettle | 1500        |
| Kitchen      | Electric Stove  | 1000        |
| Kitchen      | Dishwasher      | 1800        |
| Kitchen      | Lights          | 15          |
| Kitchen      | Fan             | 60          |
| Kitchen      | Water Dispenser | 500         |
| Dining Area  | Fan             | 60          |
| Dining Area  | Lights          | 15          |
| Dining Area  | Charger         | 10          |
| Dining Area  | Aircon          | 1500        |
| Living Room  | TV              | 150         |
| Living Room  | Aircon          | 1500        |
| Living Room  | Fan             | 60          |
| Living Room  | Lights          | 15          |
| Living Room  | Charger         | 10          |
| Bedroom      | Charger         | 10          |
| Bedroom      | Lights          | 15          |
| Bedroom      | Aircon          | 1500        |
| Bedroom      | Fan             | 60          |
| Bedroom      | Lamp            | 40          |

### Usage Level Input
```
HOW OFTEN DO YOU USE THIS APPLIANCE?
  [1] Heavy   â€” 8+ hours/day
  [2] Moderate â€” 2 to 8 hours/day
  [3] Eco      â€” Less than 2 hours/day
```

Usage hours used for calculation:
- Heavy: 8 hours/day
- Moderate: 4 hours/day
- Eco: 1 hour/day

---

## Computation

### Formula
```
kWh per month = (Wattage Ã— Hours per Day Ã— 30) / 1000
Cost per appliance = kWh Ã— PHP rate per kWh
```

> Use a **configurable rate** (default: **â‚±12.00 per kWh**, based on Meralco average).

### Monthly Cost Summary
- Sum all appliance costs across all rooms
- Compare against user-set budget
- Display `UNDER BUDGET âœ“` or `OVER BUDGET âœ—`

---

## Data Storage

### Save Format
Records must be saved to a plain text or CSV file named:

```
household_records.csv
```

Each line represents one appliance record:
```
Room,Appliance,Wattage,UsageLevel,HoursPerDay,kWh,MonthlyCost
Kitchen,Rice Cooker,400,Moderate,4,48.0,576.0
```

### Load Behavior
- On startup, the program checks if `household_records.csv` exists
- If found, it prompts the user to load previous records
- If not found, it starts fresh

---

## Required Programming Concepts Checklist

| Concept            | Where Applied                                              |
|--------------------|------------------------------------------------------------|
| Data Types         | Wattage (int), cost (float), room names (str), budget flag (bool) |
| Operators          | Cost calculation (`*`, `/`), comparisons (`>`, `<`, `==`) |
| Control Structures | Menu navigation (`if/elif/else`), budget check             |
| Loops              | `while` for menus, `for` to iterate over appliances/rooms  |
| Functions          | `compute_cost()`, `display_dashboard()`, `save_records()`, `load_records()`, etc. |
| List Handling      | Storing appliance records, room rankings                   |
| File Handling      | Save/load using `household_records.csv`                    |
| Error Handling     | Invalid menu input, missing file, non-numeric entries      |

---

## Error Handling Requirements

Handle these cases gracefully without crashing:

| Scenario                        | Expected Behavior                              |
|---------------------------------|------------------------------------------------|
| User enters non-numeric input   | Show error message, re-prompt                  |
| User enters out-of-range option | Show "Invalid choice" and re-display menu      |
| Records file not found          | Inform user, start with empty records          |
| Records file is corrupted       | Skip bad lines, notify user, continue loading  |
| No appliances added yet         | Show "No records yet" in dashboard             |
| Budget not set                  | Skip budget comparison, prompt to set one      |

---

## Expected Submission

Each group must submit:
- `main.py` â€” Main Python entry point
- `household_records.csv` â€” Sample saved records file
- `documentation.txt` â€” Short documentation (see below)
- Slides presentation file

---

## Documentation Requirements (`documentation.txt`)

Include the following sections:

1. **Project Title** â€” WattzUp: Electricity Consumption Monitoring System
2. **Group Members** â€” Names of all 4 members
3. **Brief Description** â€” What the system does
4. **Objectives** â€” Goals of the project
5. **Features and Functionalities** â€” List of main features
6. **Programming Concepts Applied** â€” How each required concept was used
7. **File Handling Explanation** â€” How `household_records.csv` is used
8. **Error Handling Explanation** â€” What errors are caught and how
9. **How to Run** â€” Step-by-step instructions to execute the program

---

## Grading Rubric (100 Points)

| Criteria                          | Description                                                                 | Points |
|-----------------------------------|-----------------------------------------------------------------------------|--------|
| Functionality                     | System works correctly; all features are operational                        | 25     |
| Code Quality and Organization     | Clean, readable, properly indented, follows Python best practices           | 15     |
| Implementation of Required Concepts | All required concepts correctly applied                                   | 20     |
| Error Handling and Robustness     | Handles invalid inputs, exceptions, missing files without crashing          | 10     |
| Creativity / Innovation           | Original, practical, and thoughtfully designed                              | 10     |
| Documentation / Explanation       | Complete, clear, explains system and concept implementation                 | 10     |
| Team Collaboration                | Balanced participation and teamwork during development and presentation     | 10     |
| **Total**                         |                                                                             | **100**|

---

## How to Run

```bash
python main.py
```

> Requires Python 3.x. No external libraries needed â€” uses only Python built-ins.

---

## Additional Instructions
- This is a group activity following your existing Terminal Requirement groupings.
- Only the group leader needs to submit on Canvas.
- The project must be original and made specifically for this course.
- Plagiarism is strictly prohibited.

