from pawpal_system import Owner, Task, Pet, Scheduler
from datetime import datetime

# Create an owner and two pets
jon = Owner("Jon")
odie = Pet("Odie", "Dachsund", 4, 20.0, [])
garfield = Pet("Garfield", "Orange Tabby", 4, 25.0, [])


# Attach pets to owner
jon.add_pet(odie)
jon.add_pet(garfield)


# Add three tasks with different times to pets
morning_walk = Task(
    "Morning Walk w/ Odie",
    1,
    datetime(2026, 2, 12, 9, 0),
    datetime(2026, 2, 12, 9, 30))
odie.add_task(morning_walk)

change_litter = Task(
    "Change Garfield's litter",
    1,
    datetime(2026, 2, 12, 10, 0),
    datetime(2026, 2, 12, 10, 5))
garfield.add_task(change_litter)

feed_garfield = Task(
    "Feed Garfield",
    1,
    datetime(2026, 2, 12, 10, 30),
    datetime(2026, 2, 12, 10, 40))
garfield.add_task(feed_garfield)


# Print "Today's Schedule" to the terminal
scheduler = Scheduler()
task_plan = scheduler.create_plan(jon)
explanation = scheduler.explain_plan(task_plan)


print("Today's Schedule:\n")
print(task_plan)
print("\n")
print(explanation)