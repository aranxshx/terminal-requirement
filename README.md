# Project Title

WattzUp: Electricity Consumption Monitoring System

# Group Members

1. [Member 1 Name]
2. [Member 2 Name]
3. [Member 3 Name]
4. [Member 4 Name]

# Brief Description

WattzUp is a Python terminal-based application for monitoring household electricity consumption. It allows users to create or continue a personal record, add appliance usage entries by room, estimate monthly electricity cost, view rankings for appliances and rooms, and manage saved records for each user.

# Objectives of the Project

1. Build a practical terminal program for tracking household electricity usage.
2. Compute monthly energy consumption and estimated cost based on appliance wattage and usage level.
3. Organize appliance records per user so different users can keep separate data.
4. Apply core Python concepts such as functions, control flow, file handling, and input validation.
5. Provide a simple interface for viewing appliances, rankings, budget status, saving, and loading records.

# Features and Functionalities

1. Startup flow to create a new user record or continue an existing one.
2. Case-insensitive username validation to prevent duplicate user records such as `Jake` and `jake`.
3. Per-user record storage inside the `data/` folder.
4. Manage Household submenu for viewing current appliances, adding new appliances, or returning to the dashboard.
5. Room and appliance selection menus for entering new appliance usage records.
6. Automatic computation of kWh and monthly electricity cost.
7. Immediate saving whenever a new appliance is added.
8. Appliance usage ranking view based on monthly cost.
9. Room usage ranking view based on monthly cost.
10. Monthly budget input and dashboard budget status display.
11. Manual save, manual load, and autosave prompt on exit.

# Programming Concepts Applied

## Functional

The program uses many small functions with clear responsibilities, such as cost computation, ranking, record parsing, saving, and loading. This keeps the logic modular and reusable.

## Procedural

The overall program flow is procedural. It follows a step-by-step menu-driven structure using conditional statements, loops, and function calls to guide the user through startup, dashboard actions, and household management.

## Object-Oriented

The project does not primarily use object-oriented design because it does not define custom classes for users or appliances. Instead, it uses dictionaries and lists to represent records and appliance data. This means the implementation is mostly procedural with some functional decomposition rather than class-based architecture.

# Explanation of File Handling Implemented

The program stores user records as text files inside the `data/` folder. Each username has its own file named using the format `data/<username>_household_records.txt`.

When a user continues an existing record, the program reads that file, parses each line, validates the contents, and converts valid rows into record dictionaries. Invalid or malformed lines are skipped so the program can continue running safely.

When a new appliance is added, the updated record list is immediately written back to the user's file. The program also supports manual save and load actions from the dashboard, and it can autosave on exit.

# Instructions of How to Run the Program

1. Open a terminal in the project folder.
2. Run `python wattzup.py`.
3. At startup, choose whether to create a new record or continue an existing one.
4. If creating a new record, enter a unique username.
5. If continuing, select an existing user record from the list.
6. Use the dashboard menu to manage appliances, view rankings, set a budget, save, load, or exit the program.
