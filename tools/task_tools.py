# note: Import tools for safely working with JARVIS's
# local task-storage file and task timestamps.
import json
from datetime import datetime
from pathlib import Path

from tools.registry import register_tool


# note: Define the approved task-storage location relative
# to the JARVIS project instead of the current terminal directory.
PROJECT_ROOT = Path(
    __file__
).resolve().parent.parent

TASKS_DIRECTORY = (
    PROJECT_ROOT
    / "tasks"
)

TASKS_FILE = (
    TASKS_DIRECTORY
    / "tasks.json"
)


# note: Define basic limits and approved values for task data
# so malformed requests fail closed.
MAX_TASK_TITLE_LENGTH = 500
MAX_TASK_SEARCH_LENGTH = 200
MAX_TASK_SEARCH_RESULTS = 20

VALID_TASK_STATUSES = {
    "open",
    "completed"
}


# note: Create the approved task-storage directory and empty
# task database if they do not already exist.
def ensure_task_storage():

    """Ensure JARVIS's local task storage exists."""

    TASKS_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True
    )

    if not TASKS_FILE.exists():

        TASKS_FILE.write_text(
            json.dumps(
                {
                    "tasks": []
                },
                indent=2
            ),
            encoding="utf-8"
        )


# note: Load the complete local task database and fail closed
# if its basic structure is invalid.
def load_tasks():

    """Load JARVIS's local task database."""

    ensure_task_storage()

    try:

        task_data = json.loads(
            TASKS_FILE.read_text(
                encoding="utf-8"
            )
        )

    except json.JSONDecodeError as error:

        raise ValueError(
            "The JARVIS task database contains invalid JSON."
        ) from error

    if not isinstance(
        task_data,
        dict
    ):

        raise ValueError(
            "The JARVIS task database must contain a JSON object."
        )

    tasks = task_data.get(
        "tasks"
    )

    if not isinstance(
        tasks,
        list
    ):

        raise ValueError(
            "The JARVIS task database must contain a tasks list."
        )

    return task_data


# note: Save the complete task database only to JARVIS's
# approved local task-storage file.
def save_tasks(
    task_data
):

    """Save JARVIS's local task database."""

    if not isinstance(
        task_data,
        dict
    ):

        raise ValueError(
            "Task data must be a dictionary."
        )

    tasks = task_data.get(
        "tasks"
    )

    if not isinstance(
        tasks,
        list
    ):

        raise ValueError(
            "Task data must contain a tasks list."
        )

    ensure_task_storage()

    TASKS_FILE.write_text(
        json.dumps(
            task_data,
            indent=2
        ),
        encoding="utf-8"
    )


# note: Determine the next local task ID without trusting the
# user or language model to choose identifiers.
def get_next_task_id(
    tasks
):

    """Return the next available numeric task ID."""

    existing_ids = []

    for task in tasks:

        if not isinstance(
            task,
            dict
        ):
            continue

        task_id = task.get(
            "id"
        )

        if (
            isinstance(task_id, int)
            and not isinstance(task_id, bool)
            and task_id > 0
        ):

            existing_ids.append(
                task_id
            )

    if not existing_ids:

        return 1

    return max(
        existing_ids
    ) + 1


# note: Validate an optional due date using a strict YYYY-MM-DD
# format so natural-language dates are not guessed at this layer.
def validate_due_date(
    due_date
):

    """Validate and normalize an optional task due date."""

    if due_date is None:

        return None

    if not isinstance(
        due_date,
        str
    ):

        raise ValueError(
            "Task due date must be text or None."
        )

    cleaned_due_date = due_date.strip()

    if not cleaned_due_date:

        raise ValueError(
            "Task due date cannot be blank."
        )

    try:

        parsed_due_date = datetime.strptime(
            cleaned_due_date,
            "%Y-%m-%d"
        )

    except ValueError as error:

        raise ValueError(
            "Task due date must use YYYY-MM-DD format."
        ) from error

    return parsed_due_date.strftime(
        "%Y-%m-%d"
    )


# note: Validate a task ID strictly so state-changing actions
# cannot rely on fuzzy matching, titles, or model interpretation.
def validate_task_id(
    task_id
):

    """Validate and normalize a local task ID."""

    if (
        not isinstance(
            task_id,
            int
        )
        or isinstance(
            task_id,
            bool
        )
    ):

        raise ValueError(
            "Task ID must be a positive integer."
        )

    if task_id <= 0:

        raise ValueError(
            "Task ID must be a positive integer."
        )

    return task_id


# note: Validate a task-search query before it is used to
# inspect stored task titles.
def validate_task_search_query(
    query
):

    """Validate and normalize a task-search query."""

    if not isinstance(
        query,
        str
    ):

        raise ValueError(
            "Task search query must be text."
        )

    cleaned_query = query.strip()

    if not cleaned_query:

        raise ValueError(
            "Task search query cannot be empty."
        )

    if len(
        cleaned_query
    ) > MAX_TASK_SEARCH_LENGTH:

        raise ValueError(
            f"Task search query cannot exceed {MAX_TASK_SEARCH_LENGTH} characters."
        )

    return cleaned_query


# note: Validate task-status filters against a small approved
# set instead of accepting arbitrary state names.
def validate_task_status(
    status
):

    """Validate and normalize a task status."""

    if not isinstance(
        status,
        str
    ):

        raise ValueError(
            "Task status must be text."
        )

    cleaned_status = status.strip().lower()

    if cleaned_status not in VALID_TASK_STATUSES:

        raise ValueError(
            "Task status must be open or completed."
        )

    return cleaned_status


# note: Create one local task after validating its title and
# optional due date. Permission enforcement is handled by
# JARVIS's registry before this function is executed.
def create_task(
    title,
    due_date=None
):

    """Create a new JARVIS task."""

    if not isinstance(
        title,
        str
    ):

        raise ValueError(
            "Task title must be text."
        )

    cleaned_title = title.strip()

    if not cleaned_title:

        raise ValueError(
            "Task title cannot be empty."
        )

    if len(
        cleaned_title
    ) > MAX_TASK_TITLE_LENGTH:

        raise ValueError(
            f"Task title cannot exceed {MAX_TASK_TITLE_LENGTH} characters."
        )

    cleaned_due_date = validate_due_date(
        due_date
    )

    task_data = load_tasks()

    tasks = task_data[
        "tasks"
    ]

    task = {
        "id": get_next_task_id(
            tasks
        ),
        "title": cleaned_title,
        "status": "open",
        "created_at": datetime.now().isoformat(
            timespec="seconds"
        ),
        "due_date": cleaned_due_date
    }

    tasks.append(
        task
    )

    save_tasks(
        task_data
    )

    return task


# note: Return the locally stored tasks without changing
# task state or requiring confirmation.
def list_tasks():

    """Return JARVIS's local task list."""

    task_data = load_tasks()

    tasks = task_data[
        "tasks"
    ]

    return {
        "count": len(
            tasks
        ),
        "tasks": tasks
    }


# note: Search task titles case-insensitively and return only
# bounded read-only result data.
def search_tasks(
    query
):

    """Search JARVIS tasks by title text."""

    cleaned_query = validate_task_search_query(
        query
    )

    lowered_query = cleaned_query.lower()

    task_data = load_tasks()

    matches = []

    for task in task_data[
        "tasks"
    ]:

        if not isinstance(
            task,
            dict
        ):
            continue

        title = task.get(
            "title"
        )

        if not isinstance(
            title,
            str
        ):
            continue

        if lowered_query not in title.lower():
            continue

        matches.append(
            {
                "id": task.get(
                    "id"
                ),
                "title": title,
                "status": task.get(
                    "status"
                ),
                "due_date": task.get(
                    "due_date"
                )
            }
        )

        if len(
            matches
        ) >= MAX_TASK_SEARCH_RESULTS:
            break

    return {
        "query": cleaned_query,
        "count": len(
            matches
        ),
        "matches": matches
    }


# note: Return only tasks with one approved status without
# changing task data.
def filter_tasks(
    status
):

    """Filter JARVIS tasks by status."""

    cleaned_status = validate_task_status(
        status
    )

    task_data = load_tasks()

    matches = []

    for task in task_data[
        "tasks"
    ]:

        if not isinstance(
            task,
            dict
        ):
            continue

        if task.get(
            "status"
        ) != cleaned_status:
            continue

        matches.append(
            {
                "id": task.get(
                    "id"
                ),
                "title": task.get(
                    "title"
                ),
                "status": task.get(
                    "status"
                ),
                "created_at": task.get(
                    "created_at"
                ),
                "due_date": task.get(
                    "due_date"
                ),
                "completed_at": task.get(
                    "completed_at"
                )
            }
        )

    return {
        "status": cleaned_status,
        "count": len(
            matches
        ),
        "tasks": matches
    }


# note: Mark one exact task as completed while preserving it
# in local history instead of deleting it.
def complete_task(
    task_id
):

    """Mark one JARVIS task as completed."""

    cleaned_task_id = validate_task_id(
        task_id
    )

    task_data = load_tasks()

    tasks = task_data[
        "tasks"
    ]

    matching_task = None

    for task in tasks:

        if not isinstance(
            task,
            dict
        ):
            continue

        if task.get(
            "id"
        ) == cleaned_task_id:

            matching_task = task
            break

    if matching_task is None:

        raise FileNotFoundError(
            "The requested task was not found."
        )

    if matching_task.get(
        "status"
    ) == "completed":

        raise ValueError(
            "The requested task is already completed."
        )

    if matching_task.get(
        "status"
    ) != "open":

        raise ValueError(
            "The requested task is not in an open state."
        )

    matching_task[
        "status"
    ] = "completed"

    matching_task[
        "completed_at"
    ] = datetime.now().isoformat(
        timespec="seconds"
    )

    save_tasks(
        task_data
    )

    return matching_task


# note: Permanently remove one exact task ID from JARVIS's
# local task list after permission has been granted.
def delete_task(
    task_id
):

    """Delete one exact JARVIS task."""

    cleaned_task_id = validate_task_id(
        task_id
    )

    task_data = load_tasks()

    tasks = task_data[
        "tasks"
    ]

    matching_index = None

    for index, task in enumerate(
        tasks
    ):

        if not isinstance(
            task,
            dict
        ):
            continue

        if task.get(
            "id"
        ) == cleaned_task_id:

            matching_index = index
            break

    if matching_index is None:

        raise FileNotFoundError(
            "The requested task was not found."
        )

    deleted_task = tasks.pop(
        matching_index
    )

    save_tasks(
        task_data
    )

    return deleted_task


# note: Register task creation as a state-changing action that
# always requires explicit permission before execution.
register_tool(
    name="create_task",
    description="Create a new task in JARVIS's local task list.",
    permission_level="confirm_required",
    function=create_task
)


# note: Register task listing as a read-only action that can
# execute without confirmation.
register_tool(
    name="list_tasks",
    description="List the tasks stored in JARVIS's local task list.",
    permission_level="safe_read",
    function=list_tasks
)


# note: Register task searching as a read-only action that can
# execute without confirmation.
register_tool(
    name="search_tasks",
    description="Search JARVIS tasks by title text.",
    permission_level="safe_read",
    function=search_tasks
)


# note: Register task filtering as a read-only action that can
# execute without confirmation.
register_tool(
    name="filter_tasks",
    description="Filter JARVIS tasks by open or completed status.",
    permission_level="safe_read",
    function=filter_tasks
)


# note: Register task completion as a state-changing action that
# requires explicit confirmation before modifying task state.
register_tool(
    name="complete_task",
    description="Mark one exact JARVIS task as completed.",
    permission_level="confirm_required",
    function=complete_task
)


# note: Register task deletion as a permanent state-changing
# action that requires explicit confirmation before execution.
register_tool(
    name="delete_task",
    description="Permanently delete one exact JARVIS task.",
    permission_level="confirm_required",
    function=delete_task
)
