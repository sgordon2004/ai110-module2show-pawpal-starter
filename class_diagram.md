# PawPal+ Class Diagram

```mermaid
classDiagram
    class Owner {
        -string name
        -Pet pet
        -int time_available
        +add_pet(Pet)
        +remove_pet()
        +add_task(Task)
        +edit_task(Task)
        +allot_time(int)
    }

    class Pet {
        -string name
        -string breed
        -int age
        -float weight
    }

    class Task {
        -string name
        -string description
        -int priority
        -datetime start_time
        -datetime end_time
    }

    class Scheduler {
        +create_plan(Owner, List~Task~)
        +explain_plan(List~Task~)
    }

    Owner "1" --> "1..*" Pet : owns
    Owner "1" --> "0..*" Task : manages
    Scheduler ..> Owner : uses
    Scheduler ..> Task : schedules
```

## Class Relationships

- **Owner → Pet**: An Owner owns one or more Pets (composition)
- **Owner → Task**: An Owner manages zero or more Tasks (aggregation)
- **Scheduler → Owner**: The Scheduler uses Owner information (dependency)
- **Scheduler → Task**: The Scheduler schedules Tasks (dependency)

## Notes

This diagram represents the initial design based on your brainstorming in reflection.md. You may need to refine this as you implement the logic and discover additional attributes or methods needed for the scheduling functionality.
