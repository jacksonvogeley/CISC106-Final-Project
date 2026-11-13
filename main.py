from drafter import *
from dataclasses import dataclass
from datetime import date, datetime

set_website_title("Assignment tracker")
set_site_information(
    author="Jackson Vogeley",
    description="Organize assignments for students.",
    sources="Thanks to the Drafter docs",
    planning=["CS1 Final Project 0 Plan.docx", "CS1 Final Project 1 Design.docx"],
    links=["https://github.com/jacksonvogeley/CISC106-Final-Project"]
)
hide_debug_information()
set_website_framed(False)


# -----------------------------------
# DATA CLASSES
# -----------------------------------

@dataclass
class Assignment:
    name: str
    course: str
    difficulty: int
    completed: bool
    due_date: str


@dataclass
class State:
    assignments: list[Assignment]
    current_assignment: Assignment
    current_date: str
    current_time: str
    courses: list[str]
    page_number: int
    message: str


# -----------------------------------
# HELPER FUNCTIONS
# -----------------------------------

def find_assignment(state, assignment_number):
    """Find an assignment using its position in the list."""
    if assignment_number >= 0 and assignment_number < len(state.assignments):
        return state.assignments[assignment_number]
    return None


def sorted_assignments(state):
    """Return assignments sorted by due date."""
    return sorted(
        state.assignments,
        key=get_due_date
    )


def days_until_due(assignment):
    """Calculate how many days remain until the due date."""
    due = date.fromisoformat(assignment.due_date)
    today = date.today()
    return (due - today).days


def get_due_date(assignment):
    return assignment.due_date


def get_difficulty(assignment):
    return assignment.difficulty


def get_recommendation(state):
    """Choose the next incomplete assignment."""
    unfinished = []

    for assignment in state.assignments:
        if assignment.completed == False:
            unfinished.append(assignment)

    if len(unfinished) == 0:
        return None

    unfinished.sort(key=get_difficulty, reverse=True)
    unfinished.sort(key=get_due_date)

    return unfinished[0]


def navigation_buttons():
    return [
        Button("Dashboard", "to_dashboard"),
        Button("All Assignments", "all_assignments"),
        Button("Incomplete Assignments", "show_uncomplete"),
        Button("Add Assignment", "add_assignment"),
        "\n"
    ]


# -----------------------------------
# DASHBOARD
# -----------------------------------

@route
def index(state: State) -> Page:
    return to_dashboard(state)


@route
def to_dashboard(state: State) -> Page:
    state.current_date = str(date.today())
    state.current_time = datetime.now().strftime("%I:%M %p")

    content = [
        Header("Student Assignment Organizer"),
        "Welcome to your assignment dashboard! \n",
        "Currrent time: " + state.current_date,
        " at " + state.current_time,
        HorizontalRule()
    ]

    content.extend(navigation_buttons())

    content.append(Header("Your Assignments"))

    if len(state.assignments) == 0:
        content.append("You have not added any assignments yet.\n")
    else:
        content.append(
            "Total assignments:" + str(len(state.assignments)) + "\n"
        )

        upcoming = sorted_assignments(state)

        # Show up to three upcoming assignments.
        for assignment in upcoming[:3]:
            content.append(
                assignment.name + " - Due: " + assignment.due_date + "\n"
            )

        content.append(Header("What Should I Do Next?"))

        recommendation = get_recommendation(state)

        if recommendation == None:
            content.append("You have completed all your assignments!\n")
        else:
            content.append(
                "Recommended: " + recommendation.name
            )
            content.append(
                "| Course: " + recommendation.course
            )
            content.append(
                "| Difficulty: " + str(recommendation.difficulty)
            )
            content.append(
                "| Due: " + recommendation.due_date + "\n"
            )

        completed_count = 0

        for assignment in state.assignments:
            if assignment.completed:
                completed_count += 1

        content.append(
            "Completed: " + str(completed_count)
            + " out of " + str(len(state.assignments))
        )

    return Page(state, content)

# -----------------------------------
# ALL ASSIGNMENTS
# -----------------------------------

@route
def all_assignments(state: State) -> Page:
    content = [
        Header("All Assignments"),
        "Your assignments, organized by due date.",
        HorizontalRule()
    ]

    content.extend(navigation_buttons())

    assignments = sorted_assignments(state)

    if len(assignments) == 0:
        content.append("You have no assignments yet.")
        return Page(state, content)

    # Display three assignments per page.
    assignments_per_page = 3
    start = state.page_number * assignments_per_page
    end = start + assignments_per_page

    for i in range(start, min(end, len(assignments))):
        assignment = assignments[i]

        content.append(Header(assignment.name))
        content.append("Course: " + assignment.course)
        content.append("| Due date: " + assignment.due_date + "\n")
        content.append("Difficulty: " + str(assignment.difficulty))

        if assignment.completed:
            content.append("| Status: Completed \n")
        else:
            content.append("| Status: Incomplete \n")

        content.append(
            Button(
                "Edit Assignment",
                "edit_assignment",
                [Argument("assignment_number", i)]
            )
        )

        content.append(
            Button(
                "Delete Assignment",
                "delete",
                [Argument("assignment_number", i)]
            )
        )

        content.append(HorizontalRule())

    if start > 0:
        content.append(Button("Previous Page", "previous_page"))

    if end < len(assignments):
        content.append(Button("Next Page", "next_page"))

    return Page(state, content)


@route
def next_page(state: State) -> Page:
    state.page_number += 1
    return all_assignments(state)


@route
def previous_page(state: State) -> Page:
    if state.page_number > 0:
        state.page_number -= 1

    return all_assignments(state)


# -----------------------------------
# ADD ASSIGNMENT
# -----------------------------------

@route
def add_assignment(state: State) -> Page:
    content = [
        Header("Add an Assignment"),
        "Enter the information for your new assignment.",
        HorizontalRule()
    ]

    content.extend(navigation_buttons())

    content.extend([
        "Assignment name:",
        TextBox("assignment_name"),

        "\nCourse:",
        TextBox("course"),

        "\nDifficulty:",
        SelectBox("difficulty", ["1", "2", "3"]),

        "\nDue date:",
        DateInput("due_date"),

        "\nAlready completed?",
        CheckBox("completed"),
        "\n",

        Button("Save Assignment", "save_assignment")
    ])

    return Page(state, content)


@route
def save_assignment(
    state: State,
    assignment_name: str,
    course: str,
    difficulty: str,
    due_date: str,
    completed: bool
) -> Page:

    if assignment_name.strip() == "":
        state.message = "Please enter an assignment name."
        return add_assignment(state)

    elif course.strip() == "":
        state.message = "Please enter a course."
        return add_assignment(state)

    elif due_date == "":
        state.message = "Please choose a due date."
        return add_assignment(state)

    new_assignment = Assignment(
        assignment_name,
        course,
        int(difficulty),
        completed,
        due_date
    )

    state.assignments.append(new_assignment)

    if course not in state.courses:
        state.courses.append(course)

    state.message = "Assignment successfully added!"
    state.page_number = 0

    return to_dashboard(state)


# -----------------------------------
# EDIT ASSIGNMENT
# -----------------------------------

@route
def edit_assignment(state: State, assignment_number: int) -> Page:
    assignment = find_assignment(state, assignment_number)

    if assignment == None:
        return Page(state, [
            Header("Assignment Not Found"),
            Button("Back to Assignments", "all_assignments")
        ])

    state.current_assignment = assignment

    return Page(state, [
        Header("Edit Assignment"),

        "Assignment name:",
        TextBox("assignment_name", assignment.name),

        "Course:",
        TextBox("course", assignment.course),

        "Difficulty:",
        SelectBox(
            "difficulty",
            ["1", "2", "3"],
            str(assignment.difficulty)
        ),

        "Due date:",
        DateInput("due_date", assignment.due_date),

        "Completed?",
        CheckBox("completed", assignment.completed),

        Button(
            "Save Changes",
            "save_edit",
            [Argument("assignment_number", assignment_number)]
        ),

        Button("Cancel", "all_assignments")
    ])


@route
def save_edit(
    state: State,
    assignment_number: int,
    assignment_name: str,
    course: str,
    difficulty: str,
    due_date: str,
    completed: bool
) -> Page:

    assignment = find_assignment(state, assignment_number)

    if assignment == None:
        return all_assignments(state)

    if assignment_name.strip() == "" or course.strip() == "" or due_date == "":
        return edit_assignment(state, assignment_number)

    assignment.name = assignment_name
    assignment.course = course
    assignment.difficulty = int(difficulty)
    assignment.due_date = due_date
    assignment.completed = completed

    if course not in state.courses:
        state.courses.append(course)

    return all_assignments(state)


# -----------------------------------
# SHOW INCOMPLETE ASSIGNMENTS
# -----------------------------------

@route
def show_uncomplete(state: State) -> Page:
    content = [
        Header("Incomplete Assignments"),
        "These are assignments you still need to finish.",
        HorizontalRule()
    ]

    content.extend(navigation_buttons())

    found_assignment = False

    for assignment in sorted_assignments(state):
        if assignment.completed == False:
            found_assignment = True
            
            content.append(Header(assignment.name))
            content.append("Course: " + assignment.course)
            content.append("| Due: " + assignment.due_date + "\n")
            content.append("Difficulty: " + str(assignment.difficulty))

            days_left = days_until_due(assignment)

            if days_left < 0:
                content.append("| Status: Overdue by " + str(abs(days_left)) + " days\n")
            elif days_left == 0:
                content.append("| Status: Due Today\n")
            elif days_left == 1:
                content.append("| Status: Due Tommorrow\n")
            else:
                content.append("| Status: Due in " + str(days_left) + " days\n")
                

            content.append(HorizontalRule())

    if found_assignment == False:
        content.append("You have no incomplete assignments!")

    return Page(state, content)


# -----------------------------------
# DELETE ASSIGNMENT
# -----------------------------------

@route
def delete(state: State, assignment_number: int) -> Page:
    assignment = find_assignment(state, assignment_number)

    if assignment == None:
        return all_assignments(state)

    return Page(state, [
        Header("Delete Assignment?"),
        "Are you sure you want to delete "
        + assignment.name + "?",

        Button(
            "Yes, Delete",
            "confirm_delete",
            [Argument("assignment_number", assignment_number)]
        ),

        Button("No, Go Back", "all_assignments")
    ])


@route
def confirm_delete(state: State, assignment_number: int) -> Page:
    assignment = find_assignment(state, assignment_number)

    if assignment != None:
        state.assignments.remove(assignment)

    state.page_number = 0

    return all_assignments(state)


# -----------------------------------
# START THE WEBSITE
# -----------------------------------

start_server(
    State(
        assignments=[],
        current_assignment=None,
        current_date=str(date.today()),
        current_time=datetime.now().strftime("%I:%M %p"),
        courses=[],
        page_number=0,
        message=""
    )
)

