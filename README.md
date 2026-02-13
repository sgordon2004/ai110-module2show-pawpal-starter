# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Smarter Scheduling

The PawPal+ scheduler now includes intelligent features that go beyond basic task management:

**Recurring Tasks** — Tasks can repeat on a schedule (daily, weekly, biweekly, monthly). When you mark a recurring task complete, the system automatically creates the next occurrence so you never forget a repeated care routine.

**Appointment Conflict Detection** — The scheduler detects when two scheduled appointments overlap on the same day. Set a start time for appointments like vet visits or grooming to enable conflict warnings. Flexible tasks (like "feed the cat") don't trigger false positives.

**Smart Prioritization** — The schedule generator sorts tasks by priority level first, then urgency (overdue tasks rise to the top), then duration (shorter tasks first). This ensures critical care happens on time.

**Task Persistence** — All your pets, tasks, and schedules are saved to JSON and automatically restored when you restart the app. Edit or mark tasks complete without losing data.

**Schedule Separation** — Generated schedules clearly separate today's tasks from future tasks, making it easy to focus on what needs to happen now.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

### Testing Pawpwal+
The command to run tests is `python -m pytest`. The tests cover sorting correctness, recurrence logic, conflict detection, and data persistence. Based on the fact that 17/17 tests passed, I have a 5/5 confidence level in Pawpal+.