"""
PawPal+ System - A pet care task scheduling system
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List


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
    priority: int # 1-5 scale, 1 = highest, 5 = lowest
    start_time: datetime
    end_time: datetime
    completed: bool = False
    description: str = None

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
            List of scheduled tasks sorted by priority and start time
        """
        # Retrieve all tasks from pets
        all_tasks = self.get_all_pet_tasks(owner)

        # Sort tasks by priority (1=highest, 5=lowest), then by start_time
        scheduled = sorted(all_tasks, key=lambda t: (t.priority, t.start_time))

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

        total_time = sum((t.end_time - t.start_time).total_seconds() / 60 for t in tasks)

        explanation = f"Schedule Plan: {len(tasks)} tasks, {total_time:.0f} minutes total\n\n"

        for i, task in enumerate(tasks, 1):
            duration = (task.end_time - task.start_time).total_seconds() / 60
            start_str = task.start_time.strftime("%I:%M %p")
            end_str = task.end_time.strftime("%I:%M %p")

            explanation += f"{i}. {task.name} - Priority {task.priority} - {duration:.0f} min ({start_str} - {end_str})\n"
            if task.description:
                explanation += f"   {task.description}\n"

        return explanation
