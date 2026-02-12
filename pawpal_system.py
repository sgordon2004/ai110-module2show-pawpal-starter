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

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list"""
        self.tasks.append(task)


@dataclass
class Task:
    """Represents a single activity with scheduling information"""
    name: str
    description: str
    priority: int
    start_time: datetime
    end_time: datetime


@dataclass
class Owner:
    """Represents a pet owner who manages pets"""
    name: str
    time_available: int = 0
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the owner's pet list"""
        pass

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from the owner's pet list"""
        pass

    def allot_time(self, time: int) -> None:
        """Set the available time for the owner"""
        pass

    def add_task_to_pet(self, pet: Pet, task: Task) -> None:
        """Add a task to a specific pet"""
        pet.tasks.append(task)


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
            List of scheduled tasks
        """
        # Retrieve all tasks from pets
        all_tasks = self.get_all_pet_tasks(owner)
        # TODO: Implement scheduling logic
        pass

    def explain_plan(self, tasks: List[Task]) -> str:
        """
        Explain the scheduled plan in human-readable format

        Args:
            tasks: List of scheduled tasks

        Returns:
            String explanation of the plan
        """
        pass
