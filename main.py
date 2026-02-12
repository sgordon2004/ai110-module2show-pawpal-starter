from pawpal_system import Owner, Task, Pet, Scheduler, Priority, Recurrence
from datetime import datetime, time

# Create an owner and two pets
jon = Owner("Jon")
odie = Pet("Odie", "Dachsund", 4, 20.0, [])
garfield = Pet("Garfield", "Orange Tabby", 4, 25.0, [])


# Attach pets to owner
jon.add_pet(odie)
jon.add_pet(garfield)


# Add tasks with durations (in minutes)
# Recurring daily task
morning_walk = Task(
    "Morning Walk w/ Odie",
    Priority.HIGH,
    30,
    due_date=datetime.fromisoformat("2026-02-13T00:00:00"),
    recurrence=Recurrence.DAILY)  # 30 minutes, recurring daily
odie.add_task(morning_walk)

# Two tasks overlapping - test
vet_appt = Task(
    "Take Odie to Vet",
    Priority.HIGH,
    30,
    due_date=datetime.fromisoformat("2026-02-13T00:00:00"),
    start_time=time.fromisoformat("09:00:00"))
odie.add_task(vet_appt)

groom_appt = Task(
    "Take Garfield to Groomer",
    Priority.HIGH,
    30,
    due_date=datetime.fromisoformat("2026-02-13T00:00:00"),
    start_time=time.fromisoformat("09:00:00"))
odie.add_task(groom_appt)

# Recurring daily task
change_litter = Task(
    "Change Garfield's litter",
    Priority.HIGH,
    5,
    due_date=datetime.fromisoformat("2026-02-13T00:00:00"),
    recurrence=Recurrence.DAILY)  # 5 minutes, recurring daily
garfield.add_task(change_litter)

# Recurring task - feed twice daily (using custom interval)
feed_garfield = Task(
    "Feed Garfield",
    Priority.HIGH,
    10,
    recurrence=Recurrence.DAILY,
    due_date=datetime.fromisoformat("2026-02-13T00:00:00"),
    description="Feed morning and evening")  # 10 minutes
garfield.add_task(feed_garfield)

# One-time task
vet_checkup = Task(
    "Vet Checkup for Odie",
    Priority.MEDIUM,
    60,
    due_date=datetime.fromisoformat("2026-02-13T00:00:00"),
    recurrence=Recurrence.ONCE)  # One-time appointment
odie.add_task(vet_checkup)


# Print "Today's Schedule" to the terminal
scheduler = Scheduler()
task_plan = scheduler.create_plan(jon)
explanation = scheduler.explain_plan(task_plan)

warnings = scheduler.detect_conflicts(jon)
print(warnings)

print("Today's Schedule:\n")
print(task_plan)
print("\n")
print(explanation)

# Demonstrate recurring task checking
print("\n--- Recurring Task Status ---\n")
for pet in jon.pets:
    for task in pet.tasks:
        status = "Needs scheduling" if task.needs_scheduling() else "Already completed"
        recurrence_info = f" (recurs: {task.recurrence.value})" if task.recurrence != Recurrence.ONCE else " (one-time)"
        print(f"{task.name}{recurrence_info}: {status}")