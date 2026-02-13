import streamlit as st
from datetime import datetime
from pawpal_system import Owner, Pet, Scheduler, Task, Priority, Recurrence, load_owner_from_json, save_owner_to_json

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# ============ INITIALIZATION STEPS ===============
# Initialize scheduler in session state if not exists
if 'scheduler' not in st.session_state:
    st.session_state.scheduler = Scheduler()

# Load owner from JSON file on startup (if it exists and not already in session state)
if 'owner' not in st.session_state:
    loaded_owner = load_owner_from_json()
    if loaded_owner:
        st.session_state.owner = loaded_owner
        # Rebuild tasks display list from loaded owner's pets
        st.session_state.tasks = []
        for pet in loaded_owner.pets:
            for task in pet.tasks:
                st.session_state.tasks.append({
                    "pet": pet.name,
                    "title": task.name,
                    "duration_minutes": task.duration,
                    "priority": task.priority.value,
                    "recurrence": task.recurrence.value,
                    "due_date": task.due_date.strftime("%Y-%m-%d") if task.due_date else ""
                })
# ============ END OF INITIALIZATION STEPS ===========

st.title("🐾 PawPal+")

# ============ LANDING PAGE (SHOWS WHEN NO OWNER EXISTS) ==============
# Landing screen - shows when no owner exists
if 'owner' not in st.session_state:
    st.markdown("### Welcome to PawPal+!")
    st.markdown("Get started by creating your profile.")

    with st.form("create_owner"):
        owner_name = st.text_input("What's your name?", placeholder="Enter your name")
        submit = st.form_submit_button("Create Profile")

        if submit:
            if owner_name.strip():
                st.session_state.owner = Owner(owner_name.strip())
                st.success(f"Welcome, {owner_name}!")
                st.rerun()
            else:
                st.error("Please enter a valid name.")

    st.stop()  # Stop execution here, don't show the rest of the app
# ============ ENDING OF LANDING PAGE =============


# ============ MAIN APP (shows when owner exists)==================

owner = st.session_state.owner
scheduler = st.session_state.scheduler

# Owner name and reset button section
col1, col2, = st.columns([3, 1])
with col1:
    st.markdown(f"**Owner:** {owner.name}")
with col2:
    if st.button("Reset", type="secondary"):
        del st.session_state.owner
        del st.session_state.tasks
        # Delete the JSON file
        import os
        if os.path.exists("pawpal_data.json"):
            os.remove("pawpal_data.json")
        st.rerun()

# Dialog for adding a pet
@st.dialog("Add a Pet")
def add_pet_dialog():
    pet_name = st.text_input("What's your pet's name?", placeholder="Enter your pet's name")
    pet_species = st.selectbox("Species", ["Dog", "Cat", "Bird", "Other"])
    pet_age = st.number_input("How old is your pet?", min_value=0, max_value=30, value=1)
    pet_weight = st.number_input("How much does your pet weigh? (lbs)", min_value=0.0, max_value=200.0, value=10.0)

    if st.button("Add Pet", type="primary"):
        if pet_name.strip():
            new_pet = Pet(pet_name.strip(), pet_species, int(pet_age), float(pet_weight), [])
            st.session_state.owner.add_pet(new_pet)
            save_owner_to_json(st.session_state.owner)  # Save to JSON
            st.success(f"Added {pet_name}!")
            st.rerun()
        else:
            st.error("Please enter a valid name.")

# Pets section with list and add button
with st.expander("My Pets", expanded=True):
    if owner.pets:
        st.markdown("**Your Pets:**")
        for pet in owner.pets:
            col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
            with col1:
                st.write(f"🐾 **{pet.name}**")
            with col2:
                st.write(f"{pet.breed}")
            with col3:
                st.write(f"{pet.age} yrs")
            with col4:
                st.write(f"{pet.weight} lbs")
            with col5:
                if st.button("🗑️", key=f"delete_{pet.name}"):
                    owner.remove_pet(pet)
                    st.rerun()
                
    else:
        st.info("No pets yet. Add one below!")

    if st.button("➕ Add Pet"):
        add_pet_dialog()

# ========== TASKS SECTION ============
st.markdown("### Tasks")
st.caption("Add and view your tasks.")

# Load tasks list into session state
if "tasks" not in st.session_state:
    st.session_state.tasks = []

# Dialog for adding a task
@st.dialog("Add a Task")
def add_task_dialog():
    pet = st.selectbox("Pet", [pet.name for pet in owner.pets])
    task_title = st.text_input("Task Name")
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    priority = st.selectbox("Priority", ["high", "medium", "low"], index=0)
    recurrence = st.selectbox("Frequency", ["once", "daily", "weekly", "biweekly", "monthly"], index=0)
    due_date = st.date_input("Due date", value=None)
    start_time = st.time_input("Start time (optional)", value=None)

    if st.button("Add task"):
        if task_title.strip():
            # Create Task object with proper types
            task_obj = Task(
                name=task_title.strip(),
                priority=Priority(priority),
                duration=int(duration),
                due_date=datetime.combine(due_date, datetime.min.time()),
                start_time=start_time,
                recurrence=Recurrence(recurrence)
            )

            # Find the pet and add task to it
            for pet_obj in owner.pets:
                if pet_obj.name == pet:
                    pet_obj.add_task(task_obj)
                    break

            # Save to JSON
            save_owner_to_json(owner)

            # Also store in session state for display
            st.session_state.tasks.append(
                {"pet": pet, "title": task_title, "duration_minutes": int(duration), "priority": priority, "recurrence": recurrence, "due_date": str(due_date)}
            )
            st.success(f"Added task '{task_title}' to {pet}!")
        else:
            st.error("Please enter a task title.")

# Dialog for editing a task
@st.dialog("Edit Task")
def edit_task_dialog(task_to_edit):
    # Get the current pet for this task
    current_pet = next((p.name for p in owner.pets if task_to_edit in p.tasks), None)

    # Get index of current pet for selectbox
    pet_index = 0
    pet_names = [p.name for p in owner.pets]
    if current_pet in pet_names:
        pet_index = pet_names.index(current_pet)

    pet = st.selectbox("Pet", pet_names, index=pet_index)
    task_title = st.text_input("Task Name", value=task_to_edit.name)
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=task_to_edit.duration)
    priority = st.selectbox("Priority", ["high", "medium", "low"], index=["high", "medium", "low"].index(task_to_edit.priority.value))
    recurrence = st.selectbox("Frequency", ["once", "daily", "weekly", "biweekly", "monthly"], index=["once", "daily", "weekly", "biweekly", "monthly"].index(task_to_edit.recurrence.value))
    due_date = st.date_input("Due date", value=task_to_edit.due_date.date() if task_to_edit.due_date else None)
    start_time = st.time_input("Start time (optional)", value=task_to_edit.start_time if task_to_edit.start_time else None)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Save Changes"):
            if task_title.strip():
                # Update the task fields
                task_to_edit.name = task_title.strip()
                task_to_edit.priority = Priority(priority)
                task_to_edit.duration = int(duration)
                task_to_edit.due_date = datetime.combine(due_date, datetime.min.time()) if due_date else None
                task_to_edit.start_time = start_time
                task_to_edit.recurrence = Recurrence(recurrence)

                # If pet changed, move task to new pet
                if pet != current_pet:
                    for p in owner.pets:
                        if p.name == current_pet and task_to_edit in p.tasks:
                            p.tasks.remove(task_to_edit)
                        elif p.name == pet:
                            p.add_task(task_to_edit)

                # Save to JSON
                save_owner_to_json(owner)
                st.success(f"Updated '{task_title}'!")
                st.rerun()
            else:
                st.error("Please enter a task title.")
    with col2:
        if st.button("Cancel"):
            st.rerun()

if st.session_state.tasks:
    col1, col2 = st.columns(2)
    with col1:
        sort_by = st.selectbox("Sort by:", ["Due Date", "Order Entered", "Pet", "Priority", "Status"])
    with col2:
        filter_by = st.selectbox("Filter by:", ["None", "Completed", "Uncompleted", "Overdue", "Pet", "Priority", "Today", "Future"])

    # Conditional filter options
    filter_pet = None
    filter_priority = None
    if filter_by == "Pet":
        filter_pet = st.selectbox("Select pet:", [pet.name for pet in owner.pets])
    elif filter_by == "Priority":
        filter_priority = st.selectbox("Select priority:", ["HIGH", "MEDIUM", "LOW"])

    # Convert display list to actual Task objects for sorting
    task_objects = []
    for pet in owner.pets:
        task_objects.extend(pet.tasks)

    sorted_tasks = []
    match sort_by:
        case "Due Date":
            sorted_tasks = scheduler.sort_by_time(task_objects)
        case "Order Entered":
            sorted_tasks = task_objects
        case "Pet":
            sorted_tasks = sorted(task_objects, key=lambda t: next((p.name for p in owner.pets if t in p.tasks), ""))
        case "Priority":
            priority_order = {"high": 0, "medium": 1, "low": 2}
            sorted_tasks = sorted(task_objects, key=lambda t: priority_order.get(t.priority.value, 999))
        case "Status":
            sorted_tasks = sorted(task_objects, key=lambda t: t.is_overdue(), reverse=True)

    # Apply filters to sorted tasks
    filtered_tasks = []
    today = datetime.now().date()
    for task in sorted_tasks:
        include_task = True

        # Apply filter based on filter_by selection
        match filter_by:
            case "None":
                include_task = not task.completed
            case "Completed":
                include_task = task.completed
            case "Uncompleted":
                include_task = not task.completed
            case "Overdue":
                include_task = task.is_overdue()
            case "Pet":
                task_pet = next((p.name for p in owner.pets if task in p.tasks), None)
                include_task = task_pet == filter_pet and not task.completed
            case "Priority":
                include_task = task.priority.value.upper() == filter_priority and not task.completed
            case "Today":
                task_date = task.due_date.date() if task.due_date else None
                include_task = task_date == today and not task.completed
            case "Future":
                task_date = task.due_date.date() if task.due_date else None
                include_task = (task_date and task_date > today) and not task.completed

        if include_task:
            filtered_tasks.append(task)

    # Display filtered and sorted tasks
    st.markdown("**Task List:**")

    # Display column headers
    header_col1, header_col2, header_col3, header_col4, header_col5, header_col6, header_col7, header_col8, header_col9 = st.columns([2, 2, 1.5, 1.2, 1.5, 1, 1.2, 1.2, 1.2])
    with header_col1:
        st.write("**Pet**")
    with header_col2:
        st.write("**Task**")
    with header_col3:
        st.write("**Due Date**")
    with header_col4:
        st.write("**Priority**")
    with header_col5:
        st.write("**Duration**")
    with header_col6:
        st.write("**Status**")
    with header_col7:
        st.write("**Complete**")
    with header_col8:
        st.write("**Edit**")
    with header_col9:
        st.write("**Delete**")

    if filtered_tasks:
        for task in filtered_tasks:
            pet_name = next((p.name for p in owner.pets if task in p.tasks), "Unknown")
            due_date_str = task.due_date.strftime("%Y-%m-%d") if task.due_date else "No due date"
            status = "⚠️ OVERDUE" if task.is_overdue() else "On Time"

            # Create columns for task display and action buttons
            col1, col2, col3, col4, col5, col6, col7, col8, col9 = st.columns([2, 2, 1.5, 1.2, 1.5, 1, 1.2, 1.2, 1.2])

            with col1:
                st.write(f"🐾 {pet_name}")
            with col2:
                st.write(f"**{task.name}**")
            with col3:
                st.write(due_date_str)
            with col4:
                st.write(task.priority.value.upper())
            with col5:
                st.write(f"{task.duration} min")
            with col6:
                st.write(status)
            with col7:
                if st.button("✓", key=f"complete_{id(task)}", help="Mark complete"):
                    # Mark task complete and create next occurrence if recurring
                    next_task = scheduler.complete_task(owner, task)

                    # Save to JSON
                    save_owner_to_json(owner)

                    # Show feedback
                    if next_task:
                        st.success(f"✓ Completed! Next '{task.name}' scheduled for {next_task.due_date.strftime('%Y-%m-%d')}")
                    else:
                        st.success(f"✓ Completed '{task.name}'!")

                    st.rerun()
            with col8:
                if st.button("✎", key=f"edit_{id(task)}", help="Edit task"):
                    st.session_state.edit_task = task
                    st.rerun()
            with col9:
                if st.button("🗑️", key=f"delete_{id(task)}", help="Delete task"):
                    # Find the pet and remove the task
                    for pet in owner.pets:
                        if task in pet.tasks:
                            pet.tasks.remove(task)
                            break

                    # Save to JSON
                    save_owner_to_json(owner)
                    st.success(f"Deleted '{task.name}'!")
                    st.rerun()
    else:
        st.info(f"No tasks match the '{filter_by}' filter.")
else:
    st.info("No tasks yet. Add one below.")

# Handle edit task dialog
if "edit_task" in st.session_state and st.session_state.edit_task:
    edit_task_dialog(st.session_state.edit_task)
    del st.session_state.edit_task

if st.button("➕Add Task"):
    add_task_dialog()

st.divider()

st.subheader("Build Schedule")
st.caption("This button should call your scheduling logic once you implement it.")

if st.button("Generate schedule"):
    st.session_state.schedule = scheduler.create_plan(st.session_state.owner)

if "schedule" in st.session_state and st.session_state.schedule:
    st.markdown("### 📅 Your Generated Schedule")

    # # Display the explanation
    # explanation = scheduler.explain_plan(st.session_state.schedule)
    # st.info(explanation)

    # Check and display scheduling conflicts
    conflicts = scheduler.detect_conflicts(owner)
    if conflicts:
        for conflict in conflicts:
            st.warning(conflict)

    # Separate tasks into today's and future tasks
    today = datetime.now().date()
    today_tasks = []
    future_tasks = []

    for task in st.session_state.schedule:
        if task.due_date:
            task_date = task.due_date.date()
            if task_date == today and not task.completed:
                today_tasks.append(task)
            elif task_date > today and not task.completed:
                future_tasks.append(task)
        else:
            future_tasks.append(task)

    # Display today's tasks
    if today_tasks:
        st.markdown("#### 📌 Today's Tasks")
        # Display column headers
        header_col1, header_col2, header_col3, header_col4, header_col5, header_col6, header_col7, header_col8 = st.columns([1.5, 2, 1.5, 1, 1.5, 1, 1.5, 1.5])
        with header_col1:
            st.write("**Pet**")
        with header_col2:
            st.write("**Task**")
        with header_col3:
            st.write("**Due Date**")
        with header_col4:
            st.write("**Priority**")
        with header_col5:
            st.write("**Duration**")
        with header_col6:
            st.write("**Status**")
        with header_col7:
            st.write("**Complete**")
        with header_col8:
            st.write("**Edit**")

        for task in today_tasks:
            pet_name = next((p.name for p in owner.pets if task in p.tasks), "Unknown")
            due_date_str = task.due_date.strftime("%m/%d/%Y") if task.due_date else "No due date"
            is_overdue = "⚠️ OVERDUE" if task.is_overdue() else "On Time"

            col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([1.5, 2, 1.5, 1, 1.5, 1, 1.5, 1.5])
            with col1:
                st.write(f"🐾 {pet_name}")
            with col2:
                st.write(f"**{task.name}**")
            with col3:
                st.write(due_date_str)
            with col4:
                st.write(task.priority.value.upper())
            with col5:
                st.write(f"{task.duration} min")
            with col6:
                st.write(is_overdue)
            with col7:
                if st.button("✓", key=f"schedule_complete_{id(task)}", help="Mark complete"):
                    next_task = scheduler.complete_task(owner, task)
                    save_owner_to_json(owner)
                    if next_task:
                        st.success(f"✓ Completed! Next '{task.name}' scheduled for {next_task.due_date.strftime('%Y-%m-%d')}")
                    else:
                        st.success(f"✓ Completed '{task.name}'!")
                    st.rerun()
            with col8:
                if st.button("✎", key=f"schedule_edit_{id(task)}", help="Edit task"):
                    st.session_state.edit_task = task
                    st.rerun()

    # Display future tasks
    if future_tasks:
        st.markdown("#### 📅 Future Tasks")
        # Display column headers
        header_col1, header_col2, header_col3, header_col4, header_col5, header_col6, header_col7, header_col8 = st.columns([1.5, 2, 1.5, 1, 1.5, 1, 1.5, 1.5])
        with header_col1:
            st.write("**Pet**")
        with header_col2:
            st.write("**Task**")
        with header_col3:
            st.write("**Due Date**")
        with header_col4:
            st.write("**Priority**")
        with header_col5:
            st.write("**Duration**")
        with header_col6:
            st.write("**Status**")
        with header_col7:
            st.write("**Complete**")
        with header_col8:
            st.write("**Edit**")

        for task in future_tasks:
            pet_name = next((p.name for p in owner.pets if task in p.tasks), "Unknown")
            due_date_str = task.due_date.strftime("%m/%d/%Y") if task.due_date else "No due date"
            is_overdue = "⚠️ OVERDUE" if task.is_overdue() else "On Time"

            col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([1.5, 2, 1.5, 1, 1.5, 1, 1.5, 1.5])
            with col1:
                st.write(f"🐾 {pet_name}")
            with col2:
                st.write(f"**{task.name}**")
            with col3:
                st.write(due_date_str)
            with col4:
                st.write(task.priority.value.upper())
            with col5:
                st.write(f"{task.duration} min")
            with col6:
                st.write(is_overdue)
            with col7:
                if st.button("✓", key=f"schedule_complete_{id(task)}", help="Mark complete"):
                    next_task = scheduler.complete_task(owner, task)
                    save_owner_to_json(owner)
                    if next_task:
                        st.success(f"✓ Completed! Next '{task.name}' scheduled for {next_task.due_date.strftime('%Y-%m-%d')}")
                    else:
                        st.success(f"✓ Completed '{task.name}'!")
                    st.rerun()
            with col8:
                if st.button("✎", key=f"schedule_edit_{id(task)}", help="Edit task"):
                    st.session_state.edit_task = task
                    st.rerun()

    # Show message if no tasks in either category
    if not today_tasks and not future_tasks:
        st.info("No tasks to display in the schedule.")
elif st.session_state.get("schedule") is not None:
    st.info("No tasks to schedule. Add some tasks to your pets first!")
