# PawPal+ Class Diagram

```mermaid
classDiagram
    class Owner {
        -string name
        -List~Pet~ pets
        +add_pet(Pet) void
        +remove_pet(Pet) void
        +add_task_to_pet(Pet, Task) void
        +mark_complete(Task) void
    }

    class Pet {
        -string name
        -string breed
        -int age
        -float weight
        -List~Task~ tasks
        +num_tasks: int (property)
        +add_task(Task) void
    }

    class Task {
        -string name
        -Priority priority
        -int duration
        -datetime due_date
        -time start_time
        -bool completed
        -string description
        -Recurrence recurrence
        -int recurrence_days
        -datetime last_completed
        +needs_scheduling() bool
        +is_overdue() bool
    }

    class Priority {
        <<enumeration>>
        HIGH
        MEDIUM
        LOW
    }

    class Recurrence {
        <<enumeration>>
        ONCE
        DAILY
        WEEKLY
        BIWEEKLY
        MONTHLY
    }

    class Scheduler {
        +calculate_next_due_date(Task) datetime
        +create_next_recurring_task(Task) Task
        +complete_task(Owner, Task) Task
        +get_all_pet_tasks(Owner) List~Task~
        +sort_by_time(List~Task~) List~Task~
        +create_plan(Owner) List~Task~
        +explain_plan(List~Task~) string
        +detect_conflicts(Owner) List~string~
        -_tasks_overlap(Task, Task) bool
    }

    class Persistence {
        <<utility>>
        +save_owner_to_json(Owner, string) void
        +load_owner_from_json(string) Owner
        +task_to_dict(Task) dict
        +dict_to_task(dict) Task
        +pet_to_dict(Pet) dict
        +dict_to_pet(dict) Pet
        +owner_to_dict(Owner) dict
        +dict_to_owner(dict) Owner
    }

    Owner "1" --> "1..*" Pet : owns
    Pet "1" --> "0..*" Task : owns
    Task --> Priority : uses
    Task --> Recurrence : uses
    Scheduler --> Owner : analyzes
    Scheduler --> Pet : reads
    Scheduler --> Task : processes
```

## Class Relationships

- **Owner → Pet**: An Owner owns one or more Pets (composition, 1..*)
- **Pet → Task**: A Pet owns zero or more Tasks (composition, 0..*)
- **Task → Priority**: Tasks use Priority enum (HIGH, MEDIUM, LOW)
- **Task → Recurrence**: Tasks use Recurrence enum (ONCE, DAILY, WEEKLY, BIWEEKLY, MONTHLY)
- **Scheduler → Owner/Pet/Task**: The Scheduler analyzes and processes Owner data to create optimized task plans (dependencies)
- **Persistence**: Utility functions for JSON serialization/deserialization of the entire data structure

## Key Implementation Differences from Initial Design

1. **Owner**: Now manages a collection of Pets; tasks belong to Pets, not directly to Owner
2. **Pet**: Now owns a list of Tasks; added `num_tasks` property and `add_task()` method
3. **Task**:
   - Replaced `end_time` with `duration` (in minutes) and `start_time` (optional appointment time)
   - Changed `priority` from int to Priority enum
   - Added recurrence support (pattern + last_completed tracking)
   - Added `is_overdue()` and `needs_scheduling()` methods
4. **Scheduler**: Significantly expanded with methods for:
   - Recurring task management (create_next_recurring_task, complete_task)
   - Task planning and sorting (create_plan with multi-level sorting)
   - Conflict detection for scheduled appointments
   - Conflict detection only checks tasks with explicit start_times
5. **Persistence**: Added JSON serialization for entire system (new in final implementation)
