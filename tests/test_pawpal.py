import unittest
from datetime import datetime
from pawpal_system import Owner, Pet, Task


class TestPawPalSystem(unittest.TestCase):
    """Tests for the PawPal+ system"""

    def test_task_completion(self):
        """Test that mark_complete() changes the task's completed status"""
        # Create owner and pet
        owner = Owner("Test Owner")
        pet = Pet("Fluffy", "Cat", 3, 10.0, [])
        owner.add_pet(pet)

        # Create a task
        task = Task(
            "Feed Fluffy",
            1,
            datetime(2026, 2, 12, 9, 0),
            datetime(2026, 2, 12, 9, 15)
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

        # Add a task
        task1 = Task(
            "Walk Buddy",
            1,
            datetime(2026, 2, 12, 10, 0),
            datetime(2026, 2, 12, 10, 30)
        )
        pet.add_task(task1)

        # Verify task count increased to 1
        self.assertEqual(pet.num_tasks, 1)

        # Add another task
        task2 = Task(
            "Feed Buddy",
            1,
            datetime(2026, 2, 12, 12, 0),
            datetime(2026, 2, 12, 12, 15)
        )
        pet.add_task(task2)

        # Verify task count increased to 2
        self.assertEqual(pet.num_tasks, 2)


if __name__ == '__main__':
    unittest.main()
