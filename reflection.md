# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

**Three Core Actions a User Should Be Able to Perform:**
1. Add a pet
2. Schedule a walk
3. See today's tasks

- Briefly describe your initial UML design.

**Main Objects Needed:**
1. Owner
    - **Attributes:**
        - `name`
        - `pet`
        - `time_available`
    - **Methods:**
        - `add_pet`
        - `remove_pet`
        - `add_task`
        - `edit_task`
        - `allot_time`
2. Pet
    - **Attributes:**
        - `name`
        - `breed`
        - `age`
        - `weight`
3. Task
    - **Attributes:**
        - `name`
        - `description`
        - `priority`
        - `start_time`
        - `end_time`
4. Scheduler
    - **Attributes:**
        - 
    - **Methods:**
        - `create_plan`
        - `explain_plan`

**b. Design changes**

- My design changes during implementation, multiple times. One example is my Owner class; although I originally designed it with an `allot_time()` function (for the user to dictate when they are available for task completion), I decided to remove it. It made the scheduling algorithm far more complicated and extended beyond the scope of this project's MVP.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- My scheduler considers priority (high first), due date urgency (soonest/overdue first), then by duration. A task's priority is the primary sort key—-I believe that weighing the task's priority any less would defeat the purpose of allowing the user to add priority levels. Date urgency is weighted more than duration because tasks that are overdue or need to be done sooner should be pushed to the top, regardless of their duration.

**b. Tradeoffs**

- My scheduler requires explicit start times for conflict detection. It only flags conflicts when BOTH tashs have scheduled times.
- Even though this tradeoff won't catch conflicts if a start time is omitted, it is worth it because it prevents noise from flexible tasks. Spamming the user with warning messages for these tasks would defeat the purpose of including warnings in the first place. This tradeoff aligns more with user intent.

---

## 3. AI Collaboration

**a. How you used AI**

- I used Claude code during all stages of development of this project. It was helpful during the design brainstorming phase because it helped provide feedback on my design. It was also incredibly helpful during the initial coding phase, as it quickly spat out boilerplate code for me to edit the specifics of manually.
- I find that the most effective prompts are those that ask specific, granular questions, and make clear demands. Also, avoid overloading one prompt with too many demands, as this can overwhelm Claude Code and result in less accurate responses.


**b. Judgment and verification**

- When I asked Claude Code to generate code to display tasks sorted by due date, it tried to replace the code to sort by order entered. I wanted both options to exist, rather than replacing the ability to sort by order entered. Instead of immediately accpeting the change, I asked Claude Code to make a more specific edit, and then accepted its new iteration after verifying its correctness.

---

## 4. Testing and Verification

**a. What you tested**

- My tests cover sorting correctness, recurrence logic, conflict detection, and data persistence. These are important because they are the core functionalities of our app. If the sorting logic doesn't work, then PawPal is useless. Data persistence is also important since it would be very annoying for the user to have to reenter their information every time they open the app again.

**b. Confidence**

- I am fully confident that my scheduler works correctly because it passed 17/17 tests. If I had more time, I would test the following edge cases: invalid priority values, invalid reccurence patterns, a None priority value, and sorting an empty task list.

---

## 5. Reflection

**a. What went well**

- I am most satisfied with the scheduling logic of this project. I've implemented multiple ways for the user to schedule their tasks, along with a scheduler that defaults to doing the highest priority tasks first, followed by due date, and then duration.

**b. What you would improve**

- If I had another iteration, I would polish the UI. Right now, certain functions can be performed through both the task list and the generated schedule. Having multiple ways to perform the same action can be confusing for the user, and I'd like to address this issue.

**c. Key takeaway**

- I learned about the importance of planning your project architeture before starting development. Having a clear blueprint of what you're building makes it much easier to implement your app's core features.
