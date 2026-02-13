import unittest
from pawpal_system import (
    Owner, Pet, Task, Priority, Recurrence, Scheduler,
    save_owner_to_json, load_owner_from_json
)
from datetime import datetime, timedelta, time
import os
import json


class TestPawPalSystem(unittest.TestCase):
    """Tests for the PawPal+ system"""

    def test_task_completion(self):
        """Test that mark_complete() changes the task's completed status"""
        # Create owner and pet
        owner = Owner("Test Owner")
        pet = Pet("Fluffy", "Cat", 3, 10.0, [])
        owner.add_pet(pet)

        # Create a task (duration in minutes)
        task = Task(
            "Feed Fluffy",
            Priority.HIGH,
            15  # 15 minutes
        )
        pet.add_task(task)

        # Verify task starts as not completed
        self.assertFalse(task.completed)

        # Mark task as complete
        owner.mark_complete(task)

        # Verify task is now marked as completed
        self.assertTrue(task.completed)

    def test_task_addition(self):
        """Test that adding a task to a Pet increases the pet's task count"""
        # Create a pet with no tasks
        pet = Pet("Buddy", "Dog", 5, 25.0, [])

        # Verify initial task count is 0
        self.assertEqual(pet.num_tasks, 0)

        # Add a task (duration in minutes)
        task1 = Task(
            "Walk Buddy",
            Priority.HIGH,
            30  # 30 minutes
        )
        pet.add_task(task1)

        # Verify task count increased to 1
        self.assertEqual(pet.num_tasks, 1)

        # Add another task
        task2 = Task(
            "Feed Buddy",
            Priority.HIGH,
            15  # 15 minutes
        )
        pet.add_task(task2)

        # Verify task count increased to 2
        self.assertEqual(pet.num_tasks, 2)

    # ===== SORTING CORRECTNESS TESTS =====
    def test_sorting_by_priority_high_first(self):
        """Verify tasks are sorted with HIGH priority tasks first"""
        owner = Owner("Test Owner")
        pet = Pet("Fluffy", "Cat", 3, 10.0, [])
        owner.add_pet(pet)

        # Create tasks with different priorities
        task_low = Task("Low Priority Task", Priority.LOW, 10, due_date=datetime.now())
        task_high = Task("High Priority Task", Priority.HIGH, 10, due_date=datetime.now())
        task_medium = Task("Medium Priority Task", Priority.MEDIUM, 10, due_date=datetime.now())

        pet.add_task(task_low)
        pet.add_task(task_high)
        pet.add_task(task_medium)

        # Create scheduler and get plan
        scheduler = Scheduler()
        plan = scheduler.create_plan(owner)

        # Verify order: HIGH, MEDIUM, LOW
        self.assertEqual(plan[0].priority, Priority.HIGH)
        self.assertEqual(plan[1].priority, Priority.MEDIUM)
        self.assertEqual(plan[2].priority, Priority.LOW)

    def test_sorting_by_due_date_urgency_soonest_first(self):
        """Verify tasks are sorted by due date urgency (soonest/overdue first)"""
        owner = Owner("Test Owner")
        pet = Pet("Buddy", "Dog", 5, 25.0, [])
        owner.add_pet(pet)

        # Create tasks with different due dates (all same priority)
        today = datetime.now()
        tomorrow = today + timedelta(days=1)
        next_week = today + timedelta(days=7)
        yesterday = today - timedelta(days=1)

        task_tomorrow = Task("Tomorrow Task", Priority.MEDIUM, 10, due_date=tomorrow)
        task_next_week = Task("Next Week Task", Priority.MEDIUM, 10, due_date=next_week)
        task_today = Task("Today Task", Priority.MEDIUM, 10, due_date=today)
        task_overdue = Task("Overdue Task", Priority.MEDIUM, 10, due_date=yesterday)

        pet.add_task(task_tomorrow)
        pet.add_task(task_next_week)
        pet.add_task(task_today)
        pet.add_task(task_overdue)

        # Create scheduler and get plan
        scheduler = Scheduler()
        plan = scheduler.create_plan(owner)

        # Verify order: overdue, today, tomorrow, next_week
        self.assertEqual(plan[0].name, "Overdue Task")
        self.assertEqual(plan[1].name, "Today Task")
        self.assertEqual(plan[2].name, "Tomorrow Task")
        self.assertEqual(plan[3].name, "Next Week Task")

    def test_sorting_by_duration_shortest_first(self):
        """Verify tasks with same priority and due date are sorted by duration (shortest first)"""
        owner = Owner("Test Owner")
        pet = Pet("Fluffy", "Cat", 3, 10.0, [])
        owner.add_pet(pet)

        # Create tasks with same priority and due date, different durations
        task_30min = Task("30 Min Task", Priority.HIGH, 30, due_date=datetime.now())
        task_15min = Task("15 Min Task", Priority.HIGH, 15, due_date=datetime.now())
        task_60min = Task("60 Min Task", Priority.HIGH, 60, due_date=datetime.now())
        task_5min = Task("5 Min Task", Priority.HIGH, 5, due_date=datetime.now())

        pet.add_task(task_30min)
        pet.add_task(task_15min)
        pet.add_task(task_60min)
        pet.add_task(task_5min)

        # Create scheduler and get plan
        scheduler = Scheduler()
        plan = scheduler.create_plan(owner)

        # Verify order by duration: 5, 15, 30, 60
        self.assertEqual(plan[0].duration, 5)
        self.assertEqual(plan[1].duration, 15)
        self.assertEqual(plan[2].duration, 30)
        self.assertEqual(plan[3].duration, 60)

    def test_sorting_combined_priority_date_duration(self):
        """Verify multi-level sorting: priority > due date > duration"""
        owner = Owner("Test Owner")
        pet = Pet("Buddy", "Dog", 5, 25.0, [])
        owner.add_pet(pet)

        today = datetime.now()
        tomorrow = today + timedelta(days=1)

        # Create complex task set
        # High priority, tomorrow, 60 min
        task1 = Task("High-Tomorrow-60", Priority.HIGH, 60, due_date=tomorrow)
        # High priority, today, 30 min
        task2 = Task("High-Today-30", Priority.HIGH, 30, due_date=today)
        # Medium priority, today, 15 min
        task3 = Task("Medium-Today-15", Priority.MEDIUM, 15, due_date=today)
        # Low priority, today, 10 min
        task4 = Task("Low-Today-10", Priority.LOW, 10, due_date=today)

        pet.add_task(task1)
        pet.add_task(task2)
        pet.add_task(task3)
        pet.add_task(task4)

        scheduler = Scheduler()
        plan = scheduler.create_plan(owner)

        # Verify order
        self.assertEqual(plan[0].name, "High-Today-30")  # HIGH priority first
        self.assertEqual(plan[1].name, "High-Tomorrow-60")  # Then next HIGH
        self.assertEqual(plan[2].name, "Medium-Today-15")  # Then MEDIUM
        self.assertEqual(plan[3].name, "Low-Today-10")  # Then LOW

    # ===== RECURRENCE LOGIC TESTS =====
    def test_recurring_daily_task_creates_next_day_task(self):
        """Verify marking a daily task complete creates a new task for the following day"""
        owner = Owner("Test Owner")
        pet = Pet("Fluffy", "Cat", 3, 10.0, [])
        owner.add_pet(pet)

        today = datetime.now()
        tomorrow = today + timedelta(days=1)

        # Create a daily recurring task
        task = Task(
            "Daily Feeding",
            Priority.HIGH,
            15,
            due_date=today,
            recurrence=Recurrence.DAILY
        )
        pet.add_task(task)

        # Verify initial state
        self.assertEqual(pet.num_tasks, 1)
        self.assertFalse(task.completed)

        # Mark task as complete
        scheduler = Scheduler()
        next_task = scheduler.complete_task(owner, task)

        # Verify original task is marked complete
        self.assertTrue(task.completed)
        self.assertIsNotNone(task.last_completed)

        # Verify next task was created
        self.assertIsNotNone(next_task)
        self.assertEqual(next_task.name, "Daily Feeding")
        self.assertEqual(next_task.recurrence, Recurrence.DAILY)
        self.assertFalse(next_task.completed)

        # Verify next task has correct due date (tomorrow)
        next_due_date = next_task.due_date.date()
        expected_due_date = tomorrow.date()
        self.assertEqual(next_due_date, expected_due_date)

        # Verify next task was added to pet's task list
        self.assertEqual(pet.num_tasks, 2)

    def test_recurring_weekly_task_creates_next_week_task(self):
        """Verify marking a weekly task complete creates a new task for next week"""
        owner = Owner("Test Owner")
        pet = Pet("Buddy", "Dog", 5, 25.0, [])
        owner.add_pet(pet)

        today = datetime.now()
        next_week = today + timedelta(days=7)

        # Create a weekly recurring task
        task = Task(
            "Weekly Grooming",
            Priority.MEDIUM,
            60,
            due_date=today,
            recurrence=Recurrence.WEEKLY
        )
        pet.add_task(task)

        # Mark task as complete
        scheduler = Scheduler()
        next_task = scheduler.complete_task(owner, task)

        # Verify next task was created with correct due date
        self.assertIsNotNone(next_task)
        next_due_date = next_task.due_date.date()
        expected_due_date = next_week.date()
        self.assertEqual(next_due_date, expected_due_date)

    def test_non_recurring_task_does_not_create_next(self):
        """Verify marking a non-recurring task complete does NOT create a new task"""
        owner = Owner("Test Owner")
        pet = Pet("Fluffy", "Cat", 3, 10.0, [])
        owner.add_pet(pet)

        today = datetime.now()

        # Create a one-time task
        task = Task(
            "One Time Task",
            Priority.HIGH,
            30,
            due_date=today,
            recurrence=Recurrence.ONCE
        )
        pet.add_task(task)

        initial_task_count = pet.num_tasks

        # Mark task as complete
        scheduler = Scheduler()
        next_task = scheduler.complete_task(owner, task)

        # Verify no next task was created
        self.assertIsNone(next_task)
        # Verify task count did not increase
        self.assertEqual(pet.num_tasks, initial_task_count)

    def test_task_preserves_properties_in_recurrence(self):
        """Verify recurring tasks preserve name, priority, duration, and description"""
        owner = Owner("Test Owner")
        pet = Pet("Fluffy", "Cat", 3, 10.0, [])
        owner.add_pet(pet)

        today = datetime.now()

        # Create a task with all properties set
        task = Task(
            "Complex Task",
            Priority.HIGH,
            45,
            due_date=today,
            start_time=time(14, 0),
            description="This is a test task",
            recurrence=Recurrence.DAILY
        )
        pet.add_task(task)

        scheduler = Scheduler()
        next_task = scheduler.complete_task(owner, task)

        # Verify all properties are preserved
        self.assertEqual(next_task.name, task.name)
        self.assertEqual(next_task.priority, task.priority)
        self.assertEqual(next_task.duration, task.duration)
        self.assertEqual(next_task.start_time, task.start_time)
        self.assertEqual(next_task.description, task.description)
        self.assertEqual(next_task.recurrence, task.recurrence)

    # ===== CONFLICT DETECTION TESTS =====
    def test_detect_overlapping_scheduled_times(self):
        """Verify the scheduler flags overlapping time slots"""
        owner = Owner("Test Owner")
        pet = Pet("Fluffy", "Cat", 3, 10.0, [])
        owner.add_pet(pet)

        today = datetime.now()

        # Create two tasks with overlapping times on the same day
        # Task 1: 2:00 PM - 2:30 PM (30 minutes)
        task1 = Task(
            "Vet Appointment",
            Priority.HIGH,
            30,
            due_date=today,
            start_time=time(14, 0)
        )

        # Task 2: 2:15 PM - 2:45 PM (30 minutes) - overlaps with task1
        task2 = Task(
            "Bath Time",
            Priority.MEDIUM,
            30,
            due_date=today,
            start_time=time(14, 15)
        )

        pet.add_task(task1)
        pet.add_task(task2)

        scheduler = Scheduler()
        conflicts = scheduler.detect_conflicts(owner)

        # Verify a conflict was detected
        self.assertGreater(len(conflicts), 0)
        self.assertIn("Conflict", conflicts[0])
        self.assertIn("Vet Appointment", conflicts[0])
        self.assertIn("Bath Time", conflicts[0])

    def test_no_conflict_for_non_overlapping_times(self):
        """Verify scheduler does NOT flag non-overlapping time slots"""
        owner = Owner("Test Owner")
        pet = Pet("Buddy", "Dog", 5, 25.0, [])
        owner.add_pet(pet)

        today = datetime.now()

        # Create two tasks with non-overlapping times
        # Task 1: 2:00 PM - 2:30 PM
        task1 = Task(
            "Morning Walk",
            Priority.HIGH,
            30,
            due_date=today,
            start_time=time(14, 0)
        )

        # Task 2: 3:00 PM - 3:30 PM (no overlap)
        task2 = Task(
            "Evening Walk",
            Priority.MEDIUM,
            30,
            due_date=today,
            start_time=time(15, 0)
        )

        pet.add_task(task1)
        pet.add_task(task2)

        scheduler = Scheduler()
        conflicts = scheduler.detect_conflicts(owner)

        # Verify no conflict was detected
        self.assertEqual(len(conflicts), 0)

    def test_conflicts_only_checked_for_scheduled_times(self):
        """Verify scheduler only flags conflicts for tasks with explicit start times"""
        owner = Owner("Test Owner")
        pet = Pet("Fluffy", "Cat", 3, 10.0, [])
        owner.add_pet(pet)

        today = datetime.now()

        # Task 1: No start time (flexible)
        task1 = Task(
            "Flexible Task",
            Priority.HIGH,
            60,
            due_date=today
        )

        # Task 2: Has start time
        task2 = Task(
            "Scheduled Task",
            Priority.MEDIUM,
            60,
            due_date=today,
            start_time=time(14, 0)
        )

        pet.add_task(task1)
        pet.add_task(task2)

        scheduler = Scheduler()
        conflicts = scheduler.detect_conflicts(owner)

        # Verify no conflict (one task has no start time)
        self.assertEqual(len(conflicts), 0)

    def test_detect_conflicts_multiple_pets(self):
        """Verify conflict detection works correctly with multiple pets"""
        owner = Owner("Test Owner")
        pet1 = Pet("Fluffy", "Cat", 3, 10.0, [])
        pet2 = Pet("Buddy", "Dog", 5, 25.0, [])
        owner.add_pet(pet1)
        owner.add_pet(pet2)

        today = datetime.now()

        # Task from pet1: 2:00 PM - 2:30 PM
        task1 = Task(
            "Fluffy's Appointment",
            Priority.HIGH,
            30,
            due_date=today,
            start_time=time(14, 0)
        )

        # Task from pet2: 2:15 PM - 2:45 PM (overlaps)
        task2 = Task(
            "Buddy's Appointment",
            Priority.HIGH,
            30,
            due_date=today,
            start_time=time(14, 15)
        )

        pet1.add_task(task1)
        pet2.add_task(task2)

        scheduler = Scheduler()
        conflicts = scheduler.detect_conflicts(owner)

        # Verify conflict detected between different pets' tasks
        self.assertGreater(len(conflicts), 0)
        self.assertIn("Fluffy", conflicts[0])
        self.assertIn("Buddy", conflicts[0])

    # ===== DATA PERSISTENCE TESTS =====
    def test_save_and_load_owner_data_json(self):
        """Verify owner data can be saved to and loaded from JSON"""
        # Create test data
        owner = Owner("John Doe")
        pet = Pet("Fluffy", "Cat", 3, 10.0, [])
        task = Task(
            "Feed Fluffy",
            Priority.HIGH,
            15,
            due_date=datetime(2026, 2, 20, 10, 0),
            description="Daily feeding"
        )
        pet.add_task(task)
        owner.add_pet(pet)

        # Save to JSON
        test_filename = "test_pawpal_data.json"
        save_owner_to_json(owner, test_filename)

        # Verify file was created
        self.assertTrue(os.path.exists(test_filename))

        # Load from JSON
        loaded_owner = load_owner_from_json(test_filename)

        # Verify owner data
        self.assertEqual(loaded_owner.name, "John Doe")
        self.assertEqual(len(loaded_owner.pets), 1)

        # Verify pet data
        loaded_pet = loaded_owner.pets[0]
        self.assertEqual(loaded_pet.name, "Fluffy")
        self.assertEqual(loaded_pet.breed, "Cat")
        self.assertEqual(loaded_pet.age, 3)
        self.assertEqual(loaded_pet.weight, 10.0)

        # Verify task data
        loaded_task = loaded_pet.tasks[0]
        self.assertEqual(loaded_task.name, "Feed Fluffy")
        self.assertEqual(loaded_task.priority, Priority.HIGH)
        self.assertEqual(loaded_task.duration, 15)
        self.assertEqual(loaded_task.description, "Daily feeding")

        # Clean up
        os.remove(test_filename)

    def test_json_preserves_task_properties(self):
        """Verify all task properties are preserved through JSON serialization"""
        owner = Owner("Jane Doe")
        pet = Pet("Buddy", "Dog", 5, 25.0, [])

        today = datetime.now()
        task = Task(
            "Walk Buddy",
            Priority.MEDIUM,
            45,
            due_date=today,
            start_time=time(10, 30),
            completed=False,
            description="Morning walk in the park",
            recurrence=Recurrence.DAILY
        )
        pet.add_task(task)
        owner.add_pet(pet)

        # Save and load
        test_filename = "test_pawpal_properties.json"
        save_owner_to_json(owner, test_filename)
        loaded_owner = load_owner_from_json(test_filename)

        # Verify all properties
        loaded_task = loaded_owner.pets[0].tasks[0]
        self.assertEqual(loaded_task.name, "Walk Buddy")
        self.assertEqual(loaded_task.priority, Priority.MEDIUM)
        self.assertEqual(loaded_task.duration, 45)
        self.assertEqual(loaded_task.start_time, time(10, 30))
        self.assertEqual(loaded_task.completed, False)
        self.assertEqual(loaded_task.description, "Morning walk in the park")
        self.assertEqual(loaded_task.recurrence, Recurrence.DAILY)

        # Clean up
        os.remove(test_filename)

    def test_load_missing_file_returns_none(self):
        """Verify loading a non-existent file returns None"""
        result = load_owner_from_json("non_existent_file.json")
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
