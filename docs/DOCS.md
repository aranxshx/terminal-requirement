# ProgLang Terminal Project Task

## [ ] Project Title
WattzUp: Electricity Consumption Monitoring System

## [ ] Group Members
1. [Member 1 Name]
2. [Member 2 Name]
3. [Member 3 Name]
4. [Member 4 Name]

## [ ] Brief Description
WattzUp is a Python terminal app that helps users track home electricity use.  
Users can add appliance records by room, see estimated monthly cost, and save or load records.

## [ ] Objectives of the Project
1. Build a simple terminal program for electricity monitoring.
2. Help users estimate monthly electricity cost.
3. Organize appliance records per user.
4. Practice core Python concepts like functions, loops, conditions, and file handling.

## [ ] Features and Functionalities
1. Create a new record or continue an existing user record.
2. Add appliances by room and usage level (Heavy, Moderate, Eco).
3. Auto-compute kWh and monthly cost.
4. View appliance usage ranking.
5. View room usage ranking.
6. Set and check monthly budget status.
7. Save records and load records from file.
8. Prompt to save before exiting.

## [ ] Programming Concepts Applied (functional|procedural|object oriented)
**Functional:**  
The app uses many small functions with clear tasks (compute cost, save/load, ranking, display).

**Procedural:**  
The app follows a step-by-step menu flow using loops and conditional statements.

**Object-Oriented:**  
The terminal app mainly uses dictionaries and lists instead of custom classes, so it is mostly procedural and functional.

## [ ] Explanation of File Handling Implemented
The app stores user data in the `data/` folder.  
Each user has a file named like `username_household_records.txt`.

- **Save:** Writes records in CSV-style format with header and rows.
- **Load:** Reads file line by line and converts valid rows into records.
- Invalid or corrupted lines are skipped to avoid crashes.

## [ ] Instructions of How to Run the Program
1. Open terminal in the project folder.
2. Run:
   ```bash
   python wattzup.py
   ```
3. Choose to create a new record or continue an existing one.
4. Use the dashboard menu to manage appliances, rankings, budget, save, and load.
