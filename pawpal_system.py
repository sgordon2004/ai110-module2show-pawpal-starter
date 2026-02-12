"""
PawPal+ System - A pet care task scheduling system
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, time
from typing import List
from enum import Enum
import json


class Priority(str, Enum):
    """Priority levels for tasks"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Recurrence(str, Enum):
    """Recurrence patterns for tasks"""
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"


@dataclass
class Pet:
    """Represents a pet with basic information and a list of tasks"""
    name: str
    breed: str
    age: int
    weight: float
    tasks: list
    @property
    def num_tasks(self):
        return len(self.tasks)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list"""
        self.tasks.append(task)


@dataclass
class Task:
    """Represents a single activity with scheduling information"""
    name: str
    priority: Priority # high, medium, or low
    duration: int # in minutes
    due_date: datetime = None  # When the task should be done
    start_time: time = None  # Optional start time for tasks with scheduled appointments
    completed: bool = False
    description: str = None
    recurrence: Recurrence = Recurrence.ONCE
    recurrence_days: int = None  # For custom intervals like every 3 days
    last_completed: datetime = None

    def needs_scheduling(self) -> bool:
        """Check if a recurring task needs to be scheduled again"""
        if self.recurrence == Recurrence.ONCE:
            return not self.completed

        if self.last_completed is None:
            return True

        # Calculate interval based on recurrence pattern
        if self.recurrence == Recurrence.DAILY:
            interval = timedelta(days=1)
        elif self.recurrence == Recurrence.WEEKLY:
            interval = timedelta(days=7)
        elif self.recurrence == Recurrence.BIWEEKLY:
            interval = timedelta(days=14)
        elif self.recurrence == Recurrence.MONTHLY:
            interval = timedelta(days=30)
        else:
            return True

        # Check if enough time has passed since last completion
        return datetime.now() - self.last_completed >= interval

    def is_overdue(self) -> bool:
        """Check if a task is overdue based on its due date"""
        if self.due_date is None:
            return False

        # Compare dates only (not time)
        due_date_only = self.due_date.date()
        today = datetime.now().date()
        return due_date_only < today and not self.completed

@dataclass
class Owner:
    """Represents a pet owner who manages pets"""
    name: str
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the owner's pet list"""
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from the owner's pet list"""
        self.pets.remove(pet)

    def add_task_to_pet(self, pet: Pet, task: Task) -> None:
        """Add a task to a specific pet"""
        pet.tasks.append(task)
    
    def mark_complete(self, task: Task) -> None:
        """Marks a task as completed"""
        task.completed = True


class Scheduler:
    """The "brain" that retrieves, organizes, and manages tasks across pets"""

    def calculate_next_due_date(self, task: Task) -> datetime | None:
        """
        Calculate the next due date for a recurring task based on its recurrence pattern

        Args:
            task: The completed recurring task

        Returns:
            The next due date as a datetime, or None if the task is not recurring
        """
        if task.recurrence == Recurrence.ONCE or task.due_date is None:
            return None

        # Calculate the interval based on recurrence pattern
        if task.recurrence == Recurrence.DAILY:
            interval = timedelta(days=1)
        elif task.recurrence == Recurrence.WEEKLY:
            interval = timedelta(days=7)
        elif task.recurrence == Recurrence.BIWEEKLY:
            interval = timedelta(days=14)
        elif task.recurrence == Recurrence.MONTHLY:
            interval = timedelta(days=30)
        else:
            return None

        # Return the current due_date + interval
        return task.due_date + interval

    def create_next_recurring_task(self, task: Task) -> Task | None:
        """
        Create the next instance of a recurring task

        Args:
            task: The completed recurring task

        Returns:
            A new Task object for the next occurrence, or None if the task is not recurring
        """
        if task.recurrence == Recurrence.ONCE:
            return None

        next_due_date = self.calculate_next_due_date(task)
        if next_due_date is None:
            return None

        # Create a new task with the same properties but new due date
        return Task(
            name=task.name,
            priority=task.priority,
            duration=task.duration,
            due_date=next_due_date,
            start_time=task.start_time,
            completed=False,
            description=task.description,
            recurrence=task.recurrence,
            recurrence_days=task.recurrence_days,
            last_completed=None
        )

    def complete_task(self, owner: Owner, task: Task) -> Task | None:
        """
        Mark a task as complete and create the next occurrence if it's recurring

        Args:
            owner: The owner whose pet has the task
            task: The task to mark as complete

        Returns:
            The next recurring task if created, or None if the task is not recurring
        """
        # Mark the current task as completed
        task.completed = True
        task.last_completed = datetime.now()

        # If the task is recurring, create the next occurrence
        if task.recurrence != Recurrence.ONCE:
            next_task = self.create_next_recurring_task(task)
            if next_task:
                # Find the pet that has this task and add the next occurrence
                for pet in owner.pets:
                    if task in pet.tasks:
                        pet.add_task(next_task)
                        return next_task
        return None

    def sort_by_time(self, tasks: List[Task]) -> List[Task]:
        """
        Sorts tasks by due date and time (soonest first)

        Args:
            tasks: List of tasks to sort

        Returns:
            List of tasks sorted by due date (soonest first), with tasks without due dates last
        """
        def sort_key(task):
            """Sort by due date and time. None due dates go last."""
            if task.due_date is None:
                return (float('inf'), 0)  # No due date goes last
            return (task.due_date, 0)

        return sorted(tasks, key=sort_key)

    # def sort_by_pet(self, tasks: List[Task]) -> List[Task]:
    #     """
    #     Sorts tasks by pet name

    #     Args:
    #         tasks: List of tasks to sort

    #     Returns:
    #         List of tasks sorted by pet names, with tasks for the same pet grouped together
    #     """
    #     def sort_key(task):
    #         """Sort by pet name"""
    #         if task.due_date is None:
    #             return (float('inf'), 0)  # No due date goes last
    #         return (task.due_date, 0)

    #     return sorted(tasks, key=sort_key)

    def get_all_pet_tasks(self, owner: Owner) -> List[Task]:
        """
        Retrieve all tasks from all of the owner's pets

        Args:
            owner: The pet owner

        Returns:
            List of all tasks from all pets
        """
        all_tasks = []
        for pet in owner.pets:
            all_tasks.extend(pet.tasks)
        return all_tasks

    def create_plan(self, owner: Owner) -> List[Task]:
        """
        Create a schedule plan for the owner based on all pet tasks

        Args:
            owner: The pet owner

        Returns:
            List of scheduled tasks sorted by priority (high first), due date urgency (soonest/overdue first), then by duration (shortest first)
        """
        # Retrieve all tasks from pets
        all_tasks = self.get_all_pet_tasks(owner)

        # Priority order for sorting: high < medium < low
        priority_order = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}

        def sort_key(task):
            """Sort by priority, then due date urgency, then duration"""
            priority = priority_order[task.priority]

            # Calculate days until due (negative = overdue, high number = far away)
            if task.due_date is None:
                days_until_due = float('inf')  # No due date goes last
            else:
                due_date_only = task.due_date.date()
                today = datetime.now().date()
                days_until_due = (due_date_only - today).days

            duration = task.duration

            return (priority, days_until_due, duration)

        # Sort tasks by priority, then by due date urgency, then by duration
        scheduled = sorted(all_tasks, key=sort_key)

        return scheduled

    def explain_plan(self, tasks: List[Task]) -> str:
        """
        Explain the scheduled plan in human-readable format

        Args:
            tasks: List of scheduled tasks

        Returns:
            String explanation of the plan
        """
        if not tasks:
            return "No tasks scheduled."

        total_time = sum(t.duration for t in tasks)

        explanation = f"Schedule Plan: {len(tasks)} tasks, {total_time} minutes total\n\n"

        for i, task in enumerate(tasks, 1):
            explanation += f"{i}. {task.name} - Priority {task.priority} - {task.duration} min\n"
            if task.description:
                explanation += f"   {task.description}\n"

        return explanation

    def _tasks_overlap(self, task1: Task, task2: Task) -> bool:
        """
        Check if two tasks have overlapping time slots

        Args:
            task1, task2: Tasks to check for overlap

        Returns:
            True if tasks overlap in time, False otherwise
        """
        if not task1.due_date or not task2.due_date:
            return False

        # Use start_time if available, otherwise use midnight
        start_time1 = task1.start_time if task1.start_time else datetime.min.time()
        start_time2 = task2.start_time if task2.start_time else datetime.min.time()

        # Combine due_date with start_time to get full datetime
        start1 = datetime.combine(task1.due_date.date(), start_time1)
        start2 = datetime.combine(task2.due_date.date(), start_time2)

        # Calculate end times based on duration
        end1 = start1 + timedelta(minutes=task1.duration)
        end2 = start2 + timedelta(minutes=task2.duration)

        # Check for overlap: task1 starts before task2 ends AND task2 starts before task1 ends
        return start1 < end2 and start2 < end1

    def detect_conflicts(self, owner: Owner) -> List[str]:
        """
        Detect scheduling conflicts between tasks with explicit start times.
        Only checks tasks that have scheduled appointment times; flexible tasks without
        start times are not checked for conflicts.

        Args:
            owner: The pet owner

        Returns:
            List of warning messages about conflicts, empty if no conflicts
        """
        all_tasks = self.get_all_pet_tasks(owner)
        warnings = []

        # Compare each task with every other task (avoiding duplicates)
        for i, task1 in enumerate(all_tasks):
            for task2 in all_tasks[i + 1:]:
                # Only check conflicts for tasks that both have explicit start times
                if task1.start_time and task2.start_time:
                    if self._tasks_overlap(task1, task2):
                        pet1 = next((p.name for p in owner.pets if task1 in p.tasks), "Unknown")
                        pet2 = next((p.name for p in owner.pets if task2 in p.tasks), "Unknown")
                        warning = f"⚠️ Conflict: '{task1.name}' ({pet1}) overlaps with '{task2.name}' ({pet2})"
                        warnings.append(warning)

        return warnings


# JSON Serialization/Deserialization Functions

def task_to_dict(task: Task) -> dict:
    """Convert a Task object to a dictionary for JSON serialization"""
    return {
        "name": task.name,
        "priority": task.priority.value,
        "duration": task.duration,
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "start_time": task.start_time.isoformat() if task.start_time else None,
        "completed": task.completed,
        "description": task.description,
        "recurrence": task.recurrence.value,
        "recurrence_days": task.recurrence_days,
        "last_completed": task.last_completed.isoformat() if task.last_completed else None
    }


def dict_to_task(data: dict) -> Task:
    """Convert a dictionary back to a Task object"""
    return Task(
        name=data["name"],
        priority=Priority(data["priority"]),
        duration=data["duration"],
        due_date=datetime.fromisoformat(data["due_date"]) if data.get("due_date") else None,
        start_time=time.fromisoformat(data["start_time"]) if data.get("start_time") else None,
        completed=data.get("completed", False),
        description=data.get("description"),
        recurrence=Recurrence(data.get("recurrence", "once")),
        recurrence_days=data.get("recurrence_days"),
        last_completed=datetime.fromisoformat(data["last_completed"]) if data.get("last_completed") else None
    )


def pet_to_dict(pet: Pet) -> dict:
    """Convert a Pet object to a dictionary for JSON serialization"""
    return {
        "name": pet.name,
        "breed": pet.breed,
        "age": pet.age,
        "weight": pet.weight,
        "tasks": [task_to_dict(task) for task in pet.tasks]
    }


def dict_to_pet(data: dict) -> Pet:
    """Convert a dictionary back to a Pet object"""
    pet = Pet(
        name=data["name"],
        breed=data["breed"],
        age=data["age"],
        weight=data["weight"],
        tasks=[]
    )
    pet.tasks = [dict_to_task(task_data) for task_data in data.get("tasks", [])]
    return pet


def owner_to_dict(owner: Owner) -> dict:
    """Convert an Owner object to a dictionary for JSON serialization"""
    return {
        "name": owner.name,
        "pets": [pet_to_dict(pet) for pet in owner.pets]
    }


def dict_to_owner(data: dict) -> Owner:
    """Convert a dictionary back to an Owner object"""
    owner = Owner(name=data["name"])
    owner.pets = [dict_to_pet(pet_data) for pet_data in data.get("pets", [])]
    return owner


def save_owner_to_json(owner: Owner, filename: str = "pawpal_data.json") -> None:
    """Save owner and all associated data to a JSON file"""
    data = owner_to_dict(owner)
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)


def load_owner_from_json(filename: str = "pawpal_data.json") -> Owner | None:
    """Load owner and all associated data from a JSON file. Returns None if file doesn't exist."""
    try:
        with open(filename, "r") as f:
            data = json.load(f)
        return dict_to_owner(data)
    except FileNotFoundError:
        return None
