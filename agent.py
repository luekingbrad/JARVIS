# note: Import tools for working with files and JARVIS's core components.
from pathlib import Path

import ollama

from router import select_skill
# note: Import chunk retrieval and deterministic domain
# selection for controlled knowledge access.
from knowledge_retriever import (
    retrieve_knowledge_chunks,
    select_allowed_domains
)
from brain import JARVISBrain
from memory import (
    is_memory_request,
    extract_memory_text,
    add_memory,
    is_forget_request,
    extract_forget_text,
    find_matching_memories,
    remove_memory,
    is_update_memory_request,
    extract_update_memory_request,
    update_memory
)


# note: Import JARVIS's approved system tools so they
# register themselves with the tool registry.
from tools import system_tools


# note: Import JARVIS's controlled note tools so they
# register themselves with the permission system.
from tools import note_tools


# note: Import JARVIS's local task-management tools so create,
# read, search, filter, complete, and delete actions register.
from tools import task_tools


# note: Import harmless temporary tools used to test
# confirmation-required and blocked permission behavior.
from tools import permission_test_tools


# note: Import the tool-routing and execution systems.
from tools.tool_router import (
    select_tool,
    classify_tool_request,
    ROUTE_AMBIGUOUS
)

from tools.registry import execute_tool, get_tool


# note: Import JARVIS's append-only action audit system.
from tools.audit_log import log_action


# note: Import the Phase 5 action-request validator so
# malformed or inconsistent actions fail closed.
from tools.action_validator import validate_action_request


# note: Import the centralized tool-argument preparation layer
# so agent.py does not perform tool-specific extraction itself.
from tools.tool_arguments import prepare_tool_arguments


# note: Import the model-assisted tool proposer for Step 29A.
# It may recommend a registered tool when deterministic routing
# has no match, but this step does not allow proposed tools to execute.
from tools.tool_proposer import propose_tool


# note: Load a text file from the JARVIS project.
def load_file(
    path
):

    """Load a text file."""

    return Path(
        path
    ).read_text(
        encoding="utf-8"
    )


# note: Load JARVIS's core operating instructions.
def load_core_instructions():

    """Load JARVIS core instructions."""

    return load_file(
        "config/system.md"
    )


# note: Load all Markdown knowledge files from the knowledge folder.
def load_knowledge():

    """Load all Markdown knowledge files."""

    knowledge = {}

    knowledge_directory = Path(
        "knowledge"
    )


    for knowledge_file in knowledge_directory.rglob(
        "*.md"
    ):

        relative_path = knowledge_file.relative_to(
            knowledge_directory
        )


        knowledge[
            str(
                relative_path
            )
        ] = knowledge_file.read_text(
            encoding="utf-8"
        )


    return knowledge


# note: Load all Markdown skill files from the skills folder.
def load_skills():

    """Load all Markdown skill files."""

    skills = {}

    skill_directory = Path(
        "skills"
    )


    for skill_file in skill_directory.glob(
        "*.md"
    ):

        skill_name = skill_file.stem


        skills[
            skill_name
        ] = skill_file.read_text(
            encoding="utf-8"
        )


    return skills


# note: Create one consistent action-request structure that
# carries tool metadata and arguments through the action pipeline.
def create_action_request(
    tool_name,
    arguments,
    permission_level,
    original_request
):

    """Create a structured JARVIS action request."""

    return {
        "tool": tool_name,
        "arguments": arguments,
        "permission_level": permission_level,
        "request": original_request
    }


# note: Determine whether the user's response is an explicit
# approval of a currently pending action.
def is_confirmation_response(
    question
):

    """Return True only for explicit confirmation responses."""

    normalized = question.lower().strip()

    normalized = normalized.rstrip(
        ".!?"
    )


    confirmation_responses = {
        "yes",
        "yes please",
        "confirm",
        "confirmed",
        "proceed",
        "go ahead",
        "do it",
        "approve",
        "approved"
    }


    return normalized in confirmation_responses


# note: Determine whether the user's response explicitly
# cancels a currently pending action.
def is_cancellation_response(
    question
):

    """Return True for explicit cancellation responses."""

    normalized = question.lower().strip()

    normalized = normalized.rstrip(
        ".!?"
    )


    cancellation_responses = {
        "no",
        "no thanks",
        "cancel",
        "cancel it",
        "stop",
        "do not proceed",
        "don't proceed",
        "decline",
        "never mind",
        "nevermind"
    }


    return normalized in cancellation_responses


# note: Build a natural JARVIS response from the
# read-only system-information tool result.
def format_system_info_response(
    tool_result
):

    """Format system information for the user."""

    if not tool_result.get(
        "success"
    ):

        return (
            "Sir, I wasn't able to retrieve the "
            "system information."
        )


    result = tool_result.get(
        "result",
        {}
    )


    operating_system = result.get(
        "operating_system",
        "Unknown"
    )

    os_version = result.get(
        "os_version",
        "Unknown"
    )

    computer_name = result.get(
        "computer_name",
        "Unknown"
    )

    architecture = result.get(
        "architecture",
        "Unknown"
    )

    python_version = result.get(
        "python_version",
        "Unknown"
    )


    return (
        f"Sir, I am currently running on "
        f"{operating_system} {os_version}, "
        f"on {computer_name}. "
        f"The system architecture is {architecture}, "
        f"and Python {python_version} is currently in use."
    )


# note: Build a natural JARVIS response from the
# current-date-and-time tool result.
def format_datetime_response(
    tool_result
):

    """Format the current local date and time."""

    if not tool_result.get(
        "success"
    ):

        return (
            "Sir, I wasn't able to retrieve the "
            "current date and time."
        )


    result = tool_result.get(
        "result",
        {}
    )


    current_date = result.get(
        "date",
        "Unknown"
    )

    current_time = result.get(
        "time",
        "Unknown"
    )

    timezone = result.get(
        "timezone",
        "Unknown"
    )


    return (
        f"Sir, the current local date is "
        f"{current_date}, and the time is "
        f"{current_time} {timezone}."
    )


# note: Build a readable JARVIS response from the
# approved project-directory listing tool.
def format_project_directory_response(
    tool_result
):

    """Format the JARVIS project directory listing."""

    if not tool_result.get(
        "success"
    ):

        return (
            "Sir, I wasn't able to inspect the "
            "JARVIS project directory."
        )


    result = tool_result.get(
        "result",
        {}
    )

    directory = result.get(
        "directory",
        "Unknown"
    )

    items = result.get(
        "items",
        []
    )


    if not items:

        return (
            f"Sir, the project directory at "
            f"{directory} appears to be empty."
        )


    response = (
        "Sir, the JARVIS project directory "
        "contains:\n\n"
    )


    for item in items:

        item_name = item.get(
            "name",
            "Unknown"
        )

        item_type = item.get(
            "type",
            "unknown"
        )


        response += (
            f"- {item_name} ({item_type})\n"
        )


    return response.strip()


# note: Build a response for the harmless temporary
# confirmation-required test tool.
def format_confirmation_test_response(
    tool_result
):

    """Format the confirmation test result."""

    if not tool_result.get(
        "success"
    ):

        return (
            "Sir, the confirmation test action "
            "was not executed."
        )


    return (
        "The confirmation-required test action "
        "was executed successfully, Sir."
    )


# note: Build a user-facing response after the controlled
# note-writing tool attempts to create a note.
def format_note_creation_response(
    tool_result
):

    """Format a note-creation result."""

    if not tool_result.get(
        "success"
    ):

        return (
            "Sir, I wasn't able to create the note."
        )


    result = tool_result.get(
        "result",
        {}
    )


    filename = result.get(
        "filename",
        "the note"
    )


    return (
        f"The note has been created successfully, Sir. "
        f"It was saved as {filename}."
    )


# note: Build a readable response from the safe read-only
# note-listing tool result.
def format_note_list_response(
    tool_result
):

    """Format the list of saved JARVIS notes."""

    if not tool_result.get(
        "success"
    ):

        return (
            "Sir, I wasn't able to retrieve "
            "your saved notes."
        )


    result = tool_result.get(
        "result",
        {}
    )


    notes = result.get(
        "notes",
        []
    )

    count = result.get(
        "count",
        len(
            notes
        )
    )


    if not notes:

        return (
            "Sir, there are currently no saved notes."
        )


    response = (
        f"Sir, you currently have {count} saved "
        f"note{'s' if count != 1 else ''}:\n\n"
    )


    for note in notes:

        filename = note.get(
            "filename",
            "Unknown"
        )


        response += (
            f"- {filename}\n"
        )


    return response.strip()


# note: Build a readable response from one successfully
# retrieved JARVIS note without invoking the language model.
def format_note_read_response(
    tool_result
):

    """Format the contents of one saved note."""

    if not tool_result.get(
        "success"
    ):

        error = tool_result.get(
            "error",
            ""
        )


        if "not found" in error.lower():

            return (
                "Sir, I couldn't find that note."
            )


        return (
            "Sir, I wasn't able to read that note."
        )


    result = tool_result.get(
        "result",
        {}
    )


    filename = result.get(
        "filename",
        "Unknown"
    )

    content = result.get(
        "content",
        ""
    )


    if not content:

        return (
            f"Sir, {filename} is currently empty."
        )


    return (
        f"Sir, {filename} contains:\n\n"
        f"{content}"
    )


# note: Build a compact readable response from the safe
# read-only note-search tool without invoking the language model.
def format_note_search_response(
    tool_result
):

    """Format matching JARVIS note-search results."""

    if not tool_result.get(
        "success"
    ):

        return (
            "Sir, I wasn't able to search "
            "your saved notes."
        )


    result = tool_result.get(
        "result",
        {}
    )


    query = result.get(
        "query",
        ""
    )

    matches = result.get(
        "matches",
        []
    )

    count = result.get(
        "count",
        len(
            matches
        )
    )


    if not matches:

        return (
            f'Sir, I found no saved notes matching "{query}".'
        )


    response = (
        f'Sir, I found {count} saved '
        f'note{"s" if count != 1 else ""} '
        f'matching "{query}":\n\n'
    )


    for match in matches:

        filename = match.get(
            "filename",
            "Unknown"
        )

        excerpt = match.get(
            "excerpt",
            ""
        )


        response += (
            f"- {filename}\n"
        )


        if excerpt:

            response += (
                f"  {excerpt}\n"
            )


    return response.strip()


# note: Build a user-facing response after one exact JARVIS
# note has been edited through the confirmed write pipeline.
def format_note_edit_response(
    tool_result
):

    """Format a note-editing result."""

    if not tool_result.get(
        "success"
    ):

        error = tool_result.get(
            "error",
            ""
        )


        if "not found" in error.lower():

            return (
                "Sir, I couldn't find that note, so no changes "
                "were made."
            )


        return (
            "Sir, I wasn't able to edit that note."
        )


    result = tool_result.get(
        "result",
        {}
    )


    filename = result.get(
        "filename",
        "the note"
    )


    return (
        f"{filename} has been updated successfully, Sir."
    )


# note: Build a user-facing response after one exact JARVIS
# note has been permanently deleted through confirmation.
def format_note_delete_response(
    tool_result
):

    """Format a note-deletion result."""

    if not tool_result.get(
        "success"
    ):

        error = tool_result.get(
            "error",
            ""
        )


        if "not found" in error.lower():

            return (
                "Sir, I couldn't find that note, so nothing "
                "was deleted."
            )


        return (
            "Sir, I wasn't able to delete that note."
        )


    result = tool_result.get(
        "result",
        {}
    )


    filename = result.get(
        "filename",
        "the note"
    )


    return (
        f"{filename} has been deleted successfully, Sir."
    )


# note: Build a user-facing response after JARVIS creates
# one confirmed task in the local task database.
def format_task_creation_response(
    tool_result
):

    """Format a task-creation result."""

    if not tool_result.get(
        "success"
    ):

        return (
            "Sir, I wasn't able to create that task."
        )


    task = tool_result.get(
        "result",
        {}
    )


    task_id = task.get(
        "id",
        "Unknown"
    )

    title = task.get(
        "title",
        "Untitled task"
    )

    due_date = task.get(
        "due_date"
    )


    response = (
        f'Task {task_id}, "{title}", has been '
        f"created successfully, Sir."
    )


    if due_date:

        response += (
            f" It is due on {due_date}."
        )


    return response


# note: Build a readable response from the safe read-only
# task-listing tool without using the language model.
def format_task_list_response(
    tool_result
):

    """Format all locally stored tasks."""

    if not tool_result.get(
        "success"
    ):

        return (
            "Sir, I wasn't able to retrieve your tasks."
        )


    result = tool_result.get(
        "result",
        {}
    )


    tasks = result.get(
        "tasks",
        []
    )

    count = result.get(
        "count",
        len(
            tasks
        )
    )


    if not tasks:

        return (
            "Sir, there are currently no saved tasks."
        )


    response = (
        f"Sir, you currently have {count} "
        f"task{'s' if count != 1 else ''}:\n\n"
    )


    for task in tasks:

        task_id = task.get(
            "id",
            "?"
        )

        title = task.get(
            "title",
            "Untitled task"
        )

        status = task.get(
            "status",
            "unknown"
        )

        due_date = task.get(
            "due_date"
        )


        response += (
            f"- [{task_id}] {title} — {status}"
        )


        if due_date:

            response += (
                f" — due {due_date}"
            )


        response += "\n"


    return response.strip()


# note: Build a compact response from deterministic task
# title-search results.
def format_task_search_response(
    tool_result
):

    """Format matching local task-search results."""

    if not tool_result.get(
        "success"
    ):

        return (
            "Sir, I wasn't able to search your tasks."
        )


    result = tool_result.get(
        "result",
        {}
    )


    query = result.get(
        "query",
        ""
    )

    matches = result.get(
        "matches",
        []
    )

    count = result.get(
        "count",
        len(
            matches
        )
    )


    if not matches:

        return (
            f'Sir, I found no tasks matching "{query}".'
        )


    response = (
        f'Sir, I found {count} '
        f'task{"s" if count != 1 else ""} '
        f'matching "{query}":\n\n'
    )


    for task in matches:

        task_id = task.get(
            "id",
            "?"
        )

        title = task.get(
            "title",
            "Untitled task"
        )

        status = task.get(
            "status",
            "unknown"
        )

        due_date = task.get(
            "due_date"
        )


        response += (
            f"- [{task_id}] {title} — {status}"
        )


        if due_date:

            response += (
                f" — due {due_date}"
            )


        response += "\n"


    return response.strip()


# note: Build a readable response for the supported open or
# completed task-status filters.
def format_task_filter_response(
    tool_result
):

    """Format filtered local tasks."""

    if not tool_result.get(
        "success"
    ):

        return (
            "Sir, I wasn't able to filter your tasks."
        )


    result = tool_result.get(
        "result",
        {}
    )


    status = result.get(
        "status",
        "unknown"
    )

    tasks = result.get(
        "tasks",
        []
    )

    count = result.get(
        "count",
        len(
            tasks
        )
    )


    if not tasks:

        return (
            f"Sir, you currently have no {status} tasks."
        )


    response = (
        f"Sir, you currently have {count} {status} "
        f"task{'s' if count != 1 else ''}:\n\n"
    )


    for task in tasks:

        task_id = task.get(
            "id",
            "?"
        )

        title = task.get(
            "title",
            "Untitled task"
        )

        due_date = task.get(
            "due_date"
        )


        response += (
            f"- [{task_id}] {title}"
        )


        if due_date:

            response += (
                f" — due {due_date}"
            )


        response += "\n"


    return response.strip()


# note: Build a response after one exact task has been marked
# completed through the confirmed write pipeline.
def format_task_completion_response(
    tool_result
):

    """Format a task-completion result."""

    if not tool_result.get(
        "success"
    ):

        error = tool_result.get(
            "error",
            ""
        )


        if "not found" in error.lower():

            return (
                "Sir, I couldn't find that task, so nothing "
                "was changed."
            )


        if "already completed" in error.lower():

            return (
                "Sir, that task is already completed."
            )


        return (
            "Sir, I wasn't able to complete that task."
        )


    task = tool_result.get(
        "result",
        {}
    )


    task_id = task.get(
        "id",
        "Unknown"
    )

    title = task.get(
        "title",
        "the task"
    )


    return (
        f'Task {task_id}, "{title}", has been marked '
        f"completed, Sir."
    )


# note: Build a response after one exact local task has been
# permanently removed through explicit confirmation.
def format_task_delete_response(
    tool_result
):

    """Format a task-deletion result."""

    if not tool_result.get(
        "success"
    ):

        error = tool_result.get(
            "error",
            ""
        )


        if "not found" in error.lower():

            return (
                "Sir, I couldn't find that task, so nothing "
                "was deleted."
            )


        return (
            "Sir, I wasn't able to delete that task."
        )


    task = tool_result.get(
        "result",
        {}
    )


    task_id = task.get(
        "id",
        "Unknown"
    )

    title = task.get(
        "title",
        "the task"
    )


    return (
        f'Task {task_id}, "{title}", has been deleted '
        f"successfully, Sir."
    )


# note: Create JARVIS's main application and load its local resources.
def main():

    core_instructions = load_core_instructions()
    knowledge = load_knowledge()
    skills = load_skills()

    brain = JARVISBrain()


    # note: Store at most one complete action request while
    # JARVIS waits for explicit user confirmation.
    pending_action = None


    print(
        "\nJARVIS Knowledge Agent"
    )

    print(
        "\nAvailable knowledge:"
    )


    for knowledge_name in knowledge:

        print(
            f"- {knowledge_name}"
        )


    print(
        "\nAvailable skills:"
    )


    for skill_name in skills:

        print(
            f"- {skill_name}"
        )


    print(
        "\nType 'exit' to quit.\n"
    )


    # note: Start the main conversation loop.
    while True:

        question = input(
            "You: "
        )


        if question.lower().strip() == "exit":

            break


        # note: Handle explicit approval only when one complete
        # action request is currently awaiting confirmation.
        if pending_action and is_confirmation_response(
            question
        ):

            pending_tool_name = pending_action[
                "tool"
            ]

            pending_arguments = pending_action[
                "arguments"
            ]

            pending_permission_level = pending_action[
                "permission_level"
            ]


            log_action(
                tool_name=pending_tool_name,
                permission_level=pending_permission_level,
                status="confirmed",
                arguments=pending_arguments
            )


            tool_result = execute_tool(
                pending_tool_name,
                confirmed=True,
                **pending_arguments
            )


            if tool_result.get(
                "success"
            ):

                execution_details = {}


                # note: Record only the created filename for note
                # creation without duplicating note content in logs.
                if pending_tool_name == "create_note":

                    result = tool_result.get(
                        "result",
                        {}
                    )

                    filename = result.get(
                        "filename"
                    )


                    if filename:

                        execution_details[
                            "filename"
                        ] = filename


                # note: Record only the edited filename for note
                # edits so replacement content is not copied into logs.
                elif pending_tool_name == "edit_note":

                    result = tool_result.get(
                        "result",
                        {}
                    )

                    filename = result.get(
                        "filename"
                    )


                    if filename:

                        execution_details[
                            "filename"
                        ] = filename


                # note: Record only the deleted filename for note
                # deletion without storing unrelated filesystem data.
                elif pending_tool_name == "delete_note":

                    result = tool_result.get(
                        "result",
                        {}
                    )

                    filename = result.get(
                        "filename"
                    )


                    if filename:

                        execution_details[
                            "filename"
                        ] = filename


                # note: Record only the generated task ID after
                # task creation rather than duplicating task text.
                elif pending_tool_name == "create_task":

                    result = tool_result.get(
                        "result",
                        {}
                    )

                    task_id = result.get(
                        "id"
                    )


                    if task_id is not None:

                        execution_details[
                            "task_id"
                        ] = task_id


                # note: Record only the exact task ID whose status
                # changed during a confirmed completion action.
                elif pending_tool_name == "complete_task":

                    result = tool_result.get(
                        "result",
                        {}
                    )

                    task_id = result.get(
                        "id"
                    )


                    if task_id is not None:

                        execution_details[
                            "task_id"
                        ] = task_id


                # note: Record only the exact deleted task ID in the
                # execution details for destructive task deletion.
                elif pending_tool_name == "delete_task":

                    result = tool_result.get(
                        "result",
                        {}
                    )

                    task_id = result.get(
                        "id"
                    )


                    if task_id is not None:

                        execution_details[
                            "task_id"
                        ] = task_id


                log_action(
                    tool_name=pending_tool_name,
                    permission_level=pending_permission_level,
                    status="executed",
                    arguments=pending_arguments,
                    details=execution_details or None
                )


            else:

                log_action(
                    tool_name=pending_tool_name,
                    permission_level=pending_permission_level,
                    status="failed",
                    arguments=pending_arguments
                )


            pending_action = None


            if pending_tool_name == "test_confirmed_action":

                answer = format_confirmation_test_response(
                    tool_result
                )


            elif pending_tool_name == "create_note":

                answer = format_note_creation_response(
                    tool_result
                )


            elif pending_tool_name == "edit_note":

                answer = format_note_edit_response(
                    tool_result
                )


            elif pending_tool_name == "delete_note":

                answer = format_note_delete_response(
                    tool_result
                )


            elif pending_tool_name == "create_task":

                answer = format_task_creation_response(
                    tool_result
                )


            elif pending_tool_name == "complete_task":

                answer = format_task_completion_response(
                    tool_result
                )


            elif pending_tool_name == "delete_task":

                answer = format_task_delete_response(
                    tool_result
                )


            else:

                if tool_result.get(
                    "success"
                ):

                    answer = (
                        "The confirmed action was completed "
                        "successfully, Sir."
                    )

                else:

                    answer = (
                        "Sir, the confirmed action could not "
                        "be completed."
                    )


            brain.store_conversation(
                question,
                answer
            )


            print(
                f"\nJARVIS: {answer}\n"
            )

            continue


        # note: Handle explicit cancellation of the currently
        # pending action request.
        if pending_action and is_cancellation_response(
            question
        ):

            pending_tool_name = pending_action[
                "tool"
            ]

            pending_arguments = pending_action[
                "arguments"
            ]

            pending_permission_level = pending_action[
                "permission_level"
            ]


            log_action(
                tool_name=pending_tool_name,
                permission_level=pending_permission_level,
                status="canceled",
                arguments=pending_arguments
            )


            pending_action = None


            answer = (
                "Understood, Sir. The pending action "
                "has been canceled."
            )


            brain.store_conversation(
                question,
                answer
            )


            print(
                f"\nJARVIS: {answer}\n"
            )

            continue


        # note: Cancel an existing pending action request when
        # the next message is neither approval nor cancellation.
        if pending_action:

            pending_tool_name = pending_action[
                "tool"
            ]

            pending_arguments = pending_action[
                "arguments"
            ]

            pending_permission_level = pending_action[
                "permission_level"
            ]


            log_action(
                tool_name=pending_tool_name,
                permission_level=pending_permission_level,
                status="canceled",
                arguments=pending_arguments,
                details={
                    "reason": "confirmation_not_received"
                }
            )


            pending_action = None


            print(
                "\nJARVIS: Sir, the pending action has been "
                "canceled because I did not receive explicit "
                "confirmation.\n"
            )


        # note: Prevent isolated approval responses when no
        # action request is awaiting confirmation.
        if is_confirmation_response(
            question
        ):

            answer = (
                "Sir, there is currently no action "
                "awaiting your confirmation."
            )


            brain.store_conversation(
                question,
                answer
            )


            print(
                f"\nJARVIS: {answer}\n"
            )

            continue


        # note: Prevent isolated cancellation responses when
        # there is no pending action request.
        if is_cancellation_response(
            question
        ):

            answer = (
                "Sir, there is currently no pending "
                "action to cancel."
            )


            brain.store_conversation(
                question,
                answer
            )


            print(
                f"\nJARVIS: {answer}\n"
            )

            continue


        # note: Check whether the user is explicitly asking
        # JARVIS to remember something.
        if is_memory_request(
            question
        ):

            memory_text = extract_memory_text(
                question
            )


            if memory_text:

                memory_result = add_memory(
                    memory_text
                )

                memory_action = memory_result.get(
                    "action"
                )


                if memory_action == "duplicate":

                    print(
                        "\nJARVIS: Sir, I already remember "
                        "that information.\n"
                    )


                elif memory_action == "updated":

                    print(
                        f"\nJARVIS: Of course, Sir. "
                        f"I've updated that memory to: "
                        f"{memory_text}\n"
                    )


                else:

                    print(
                        f"\nJARVIS: Of course, Sir. "
                        f"I'll remember that {memory_text}\n"
                    )


            else:

                print(
                    "\nJARVIS: Sir, I wasn't able to determine "
                    "what you wanted me to remember.\n"
                )


            continue


        # note: Check whether the user explicitly asked JARVIS
        # to forget persistent information.
        if is_forget_request(
            question
        ):

            forget_text = extract_forget_text(
                question
            )


            removed_memory = remove_memory(
                forget_text
            )


            if removed_memory:

                removed_text = removed_memory.get(
                    "text",
                    forget_text
                )


                print(
                    f"\nJARVIS: Of course, Sir. "
                    f"I've forgotten that {removed_text}\n"
                )

                continue


            matching_memories = find_matching_memories(
                forget_text
            )


            if not matching_memories:

                print(
                    "\nJARVIS: Sir, I couldn't find a stored "
                    "memory matching that information.\n"
                )

                continue


            if len(
                matching_memories
            ) == 1:

                matched_memory = matching_memories[
                    0
                ][
                    "memory"
                ]

                matched_text = matched_memory.get(
                    "text",
                    ""
                )


                remove_memory(
                    matched_text
                )


                print(
                    f"\nJARVIS: Of course, Sir. "
                    f"I've forgotten that {matched_text}\n"
                )

                continue


            print(
                "\nJARVIS: Sir, I found multiple memories "
                "that could match that request, so I haven't "
                "deleted anything.\n"
            )

            continue


        # note: Check whether the user explicitly asked JARVIS
        # to update information already stored in memory.
        if is_update_memory_request(
            question
        ):

            update_request = extract_update_memory_request(
                question
            )


            if not update_request:

                print(
                    "\nJARVIS: Sir, I wasn't able to determine "
                    "which memory you wanted to update.\n"
                )

                continue


            subject = update_request[
                "subject"
            ]

            new_value = update_request[
                "new_value"
            ]


            matching_memories = find_matching_memories(
                subject
            )


            if not matching_memories:

                print(
                    "\nJARVIS: Sir, I couldn't find a stored "
                    "memory matching that information.\n"
                )

                continue


            strongest_score = matching_memories[
                0
            ][
                "score"
            ]


            strongest_matches = [
                item
                for item in matching_memories
                if item[
                    "score"
                ] == strongest_score
            ]


            if len(
                strongest_matches
            ) > 1:

                print(
                    "\nJARVIS: Sir, I found multiple memories "
                    "that could match that request, so I haven't "
                    "changed anything.\n"
                )

                continue


            matched_memory = strongest_matches[
                0
            ][
                "memory"
            ]

            old_text = matched_memory.get(
                "text",
                ""
            )


            new_text = (
                f"{subject} is {new_value}."
            )


            updated_memory = update_memory(
                old_text,
                new_text
            )


            if updated_memory:

                print(
                    f"\nJARVIS: Of course, Sir. "
                    f"I've updated that memory to: "
                    f"{new_text}\n"
                )


            else:

                print(
                    "\nJARVIS: Sir, I wasn't able to update "
                    "that memory.\n"
                )


            continue


        # note: Classify the request before normal tool selection
        # so ambiguous write or read requests stop deterministically.
        tool_classification = classify_tool_request(
            question
        )


        # note: Prevent vague note-deletion requests from falling
        # through to the LLM or causing JARVIS to guess a target.
        if (
            tool_classification.get(
                "status"
            ) == ROUTE_AMBIGUOUS
            and tool_classification.get(
                "reason"
            ) == "ambiguous_note_delete_request"
        ):

            answer = (
                "Sir, I need the exact note filename before I "
                "can delete a note. You can list or search your "
                "notes first if needed."
            )


            brain.store_conversation(
                question,
                answer
            )


            print(
                f"\nJARVIS: {answer}\n"
            )

            continue


        # note: Prevent incomplete note-edit requests from falling
        # through to the LLM or causing JARVIS to guess a write.
        if (
            tool_classification.get(
                "status"
            ) == ROUTE_AMBIGUOUS
            and tool_classification.get(
                "reason"
            ) == "ambiguous_note_edit_request"
        ):

            answer = (
                "Sir, I need the exact note filename and the "
                "replacement content before I can edit a note."
            )


            brain.store_conversation(
                question,
                answer
            )


            print(
                f"\nJARVIS: {answer}\n"
            )

            continue


        # note: Prevent incomplete note-search requests from
        # falling through to the LLM and inventing search results.
        if (
            tool_classification.get(
                "status"
            ) == ROUTE_AMBIGUOUS
            and tool_classification.get(
                "reason"
            ) == "ambiguous_note_search_request"
        ):

            answer = (
                "Sir, I need you to specify what you want me "
                "to search for in your notes."
            )


            brain.store_conversation(
                question,
                answer
            )


            print(
                f"\nJARVIS: {answer}\n"
            )

            continue


        # note: Prevent vague note commands such as "Open note."
        # from falling through to the LLM and fabricating an action.
        if (
            tool_classification.get(
                "status"
            ) == ROUTE_AMBIGUOUS
            and tool_classification.get(
                "reason"
            ) == "ambiguous_note_request"
        ):

            answer = (
                "Sir, I need you to specify which note you want "
                "me to read. You can list your notes first, then "
                "give me the exact filename."
            )


            brain.store_conversation(
                question,
                answer
            )


            print(
                f"\nJARVIS: {answer}\n"
            )

            continue


        # note: Prevent task creation without an explicit title
        # from reaching tool execution or model reasoning.
        if (
            tool_classification.get(
                "status"
            ) == ROUTE_AMBIGUOUS
            and tool_classification.get(
                "reason"
            ) == "ambiguous_task_creation_request"
        ):

            answer = (
                "Sir, I need the task title before I can create "
                "a new task."
            )


            brain.store_conversation(
                question,
                answer
            )


            print(
                f"\nJARVIS: {answer}\n"
            )

            continue


        # note: Prevent incomplete task-search requests from
        # reaching the LLM and inventing task matches.
        if (
            tool_classification.get(
                "status"
            ) == ROUTE_AMBIGUOUS
            and tool_classification.get(
                "reason"
            ) == "ambiguous_task_search_request"
        ):

            answer = (
                "Sir, I need you to specify what you want me "
                "to search for in your tasks."
            )


            brain.store_conversation(
                question,
                answer
            )


            print(
                f"\nJARVIS: {answer}\n"
            )

            continue


        # note: Reject unsupported task states rather than allowing
        # the model to reinterpret pending, active, or similar words.
        if (
            tool_classification.get(
                "status"
            ) == ROUTE_AMBIGUOUS
            and tool_classification.get(
                "reason"
            ) == "unsupported_task_status_filter"
        ):

            answer = (
                "Sir, task filtering currently supports only "
                "open or completed tasks."
            )


            brain.store_conversation(
                question,
                answer
            )


            print(
                f"\nJARVIS: {answer}\n"
            )

            continue


        # note: Task completion changes persistent state and therefore
        # requires one exact positive numeric task ID.
        if (
            tool_classification.get(
                "status"
            ) == ROUTE_AMBIGUOUS
            and tool_classification.get(
                "reason"
            ) == "ambiguous_task_completion_request"
        ):

            answer = (
                "Sir, I need the exact numeric task ID before I "
                "can mark a task completed. You can list or search "
                "your tasks first if needed."
            )


            brain.store_conversation(
                question,
                answer
            )


            print(
                f"\nJARVIS: {answer}\n"
            )

            continue


        # note: Task deletion is destructive and must never guess
        # which task the user intended to remove.
        if (
            tool_classification.get(
                "status"
            ) == ROUTE_AMBIGUOUS
            and tool_classification.get(
                "reason"
            ) == "ambiguous_task_delete_request"
        ):

            answer = (
                "Sir, I need the exact numeric task ID before I "
                "can permanently delete a task. You can list or "
                "search your tasks first if needed."
            )


            brain.store_conversation(
                question,
                answer
            )


            print(
                f"\nJARVIS: {answer}\n"
            )

            continue


        # note: Catch a bare or otherwise vague task reference so
        # it does not silently fall through to language-model reasoning.
        if (
            tool_classification.get(
                "status"
            ) == ROUTE_AMBIGUOUS
            and tool_classification.get(
                "reason"
            ) == "ambiguous_task_request"
        ):

            answer = (
                "Sir, I need a more specific task request. I can "
                "create, list, search, filter, complete, or delete "
                "tasks."
            )


            brain.store_conversation(
                question,
                answer
            )


            print(
                f"\nJARVIS: {answer}\n"
            )

            continue


        # note: Route the user's request to a supported JARVIS tool
        # before preparing any arguments or considering execution.
        selected_tool_name = select_tool(
            question
        )


        # note: Preserve the deterministic denial path for filesystem
        # requests outside JARVIS's currently approved project area.
        if selected_tool_name == "filesystem_access_denied":

            answer = (
                "Sir, I do not currently have permission to access "
                "or modify that filesystem location. My filesystem "
                "actions are limited to approved JARVIS locations."
            )


            brain.store_conversation(
                question,
                answer
            )


            print(
                f"\nJARVIS: {answer}\n"
            )

            continue


        # note: Step 29E allows a validated high-confidence model
        # proposal to become the selected tool for the existing
        # deterministic argument, permission, and execution pipeline.
        if selected_tool_name is None:

            tool_proposal = propose_tool(
                question
            )


            if (
                tool_proposal.get(
                    "valid"
                )
                and tool_proposal.get(
                    "confidence"
                ) == "high"
                and tool_proposal.get(
                    "tool"
                )
            ):

                proposed_tool_name = tool_proposal[
                    "tool"
                ]


                # note: Promote only the already validated model
                # proposal into the normal selected-tool variable.
                # The model still supplies no execution arguments
                # and receives no permission or execution authority.
                selected_tool_name = proposed_tool_name


        # note: Prepare and validate arguments through the centralized
        # tool-argument layer whenever a real tool has been selected.
        if selected_tool_name:

            argument_result = prepare_tool_arguments(
                selected_tool_name,
                question
            )


            if not argument_result.get(
                "success"
            ):

                if selected_tool_name == "create_note":

                    answer = (
                        "Sir, I understand that you want to create "
                        "a note, but I couldn't determine what you "
                        "want the note to say."
                    )


                elif selected_tool_name == "read_note":

                    answer = (
                        "Sir, I couldn't determine a valid note "
                        "filename from that request."
                    )


                elif selected_tool_name == "search_notes":

                    answer = (
                        "Sir, I understand that you want to search "
                        "your notes, but I couldn't determine what "
                        "you want me to search for."
                    )


                elif selected_tool_name == "edit_note":

                    answer = (
                        "Sir, I couldn't determine a valid exact "
                        "note filename and replacement content "
                        "from that edit request."
                    )


                elif selected_tool_name == "delete_note":

                    answer = (
                        "Sir, I couldn't determine a valid exact "
                        "JARVIS note filename from that deletion "
                        "request."
                    )


                elif selected_tool_name == "create_task":

                    answer = (
                        "Sir, I couldn't prepare that task. Please "
                        "provide a task title and, if you include a "
                        "due date, use YYYY-MM-DD format."
                    )


                elif selected_tool_name == "search_tasks":

                    answer = (
                        "Sir, I understand that you want to search "
                        "your tasks, but I couldn't determine the "
                        "search term."
                    )


                elif selected_tool_name == "filter_tasks":

                    answer = (
                        "Sir, task filtering currently supports "
                        "only open or completed."
                    )


                elif selected_tool_name == "complete_task":

                    answer = (
                        "Sir, I couldn't determine a valid positive "
                        "numeric task ID to complete."
                    )


                elif selected_tool_name == "delete_task":

                    answer = (
                        "Sir, I couldn't determine a valid positive "
                        "numeric task ID to delete."
                    )


                else:

                    answer = (
                        "Sir, I could not prepare valid arguments "
                        "for that action."
                    )


                brain.store_conversation(
                    question,
                    answer
                )


                print(
                    f"\nJARVIS: {answer}\n"
                )

                continue


            tool_arguments = argument_result.get(
                "arguments",
                {}
            )


        # note: Build and process a complete action request for
        # every selected registered tool.
        if selected_tool_name:

            registered_tool = get_tool(
                selected_tool_name
            )


            if registered_tool:

                permission_level = registered_tool.get(
                    "permission_level",
                    "unknown"
                )


            else:

                permission_level = "unregistered"


            action_request = create_action_request(
                tool_name=selected_tool_name,
                arguments=tool_arguments,
                permission_level=permission_level,
                original_request=question
            )


            validation_result = validate_action_request(
                action_request
            )


            if not validation_result.get(
                "valid"
            ):

                answer = (
                    "Sir, I could not process that action because "
                    "its action request failed validation."
                )


                brain.store_conversation(
                    question,
                    answer
                )


                print(
                    f"\nJARVIS: {answer}\n"
                )

                continue


            log_action(
                tool_name=action_request[
                    "tool"
                ],
                permission_level=action_request[
                    "permission_level"
                ],
                status="requested",
                arguments=action_request[
                    "arguments"
                ]
            )


            tool_result = execute_tool(
                action_request[
                    "tool"
                ],
                **action_request[
                    "arguments"
                ]
            )


            action_request[
                "permission_level"
            ] = tool_result.get(
                "permission_level",
                action_request[
                    "permission_level"
                ]
            )


            if tool_result.get(
                "requires_confirmation"
            ):

                pending_action = action_request


                log_action(
                    tool_name=action_request[
                        "tool"
                    ],
                    permission_level=action_request[
                        "permission_level"
                    ],
                    status="confirmation_required",
                    arguments=action_request[
                        "arguments"
                    ]
                )


                if action_request[
                    "tool"
                ] == "create_note":

                    answer = (
                        "Sir, creating this note will modify "
                        "local data. Would you like me to proceed?"
                    )


                elif action_request[
                    "tool"
                ] == "edit_note":

                    filename = action_request[
                        "arguments"
                    ].get(
                        "filename",
                        "that note"
                    )


                    answer = (
                        f"Sir, editing {filename} will replace its "
                        f"current contents. Would you like me to proceed?"
                    )


                elif action_request[
                    "tool"
                ] == "delete_note":

                    filename = action_request[
                        "arguments"
                    ].get(
                        "filename",
                        "that note"
                    )


                    answer = (
                        f"Sir, deleting {filename} will permanently "
                        f"remove that note. Would you like me to proceed?"
                    )


                elif action_request[
                    "tool"
                ] == "create_task":

                    title = action_request[
                        "arguments"
                    ].get(
                        "title",
                        "that task"
                    )

                    due_date = action_request[
                        "arguments"
                    ].get(
                        "due_date"
                    )


                    if due_date:

                        answer = (
                            f'Sir, creating the task "{title}" with '
                            f"a due date of {due_date} will modify "
                            f"your local task list. Would you like "
                            f"me to proceed?"
                        )


                    else:

                        answer = (
                            f'Sir, creating the task "{title}" will '
                            f"modify your local task list. Would you "
                            f"like me to proceed?"
                        )


                elif action_request[
                    "tool"
                ] == "complete_task":

                    task_id = action_request[
                        "arguments"
                    ].get(
                        "task_id",
                        "Unknown"
                    )


                    answer = (
                        f"Sir, this will mark task {task_id} as "
                        f"completed. Would you like me to proceed?"
                    )


                elif action_request[
                    "tool"
                ] == "delete_task":

                    task_id = action_request[
                        "arguments"
                    ].get(
                        "task_id",
                        "Unknown"
                    )


                    answer = (
                        f"Sir, deleting task {task_id} will permanently "
                        f"remove it from your local task list. Would "
                        f"you like me to proceed?"
                    )


                else:

                    answer = (
                        "Sir, this action requires your explicit "
                        "confirmation before I can execute it. "
                        "Would you like me to proceed?"
                    )


                brain.store_conversation(
                    question,
                    answer
                )


                print(
                    f"\nJARVIS: {answer}\n"
                )

                continue


            if (
                action_request[
                    "permission_level"
                ] == "blocked"
                and not tool_result.get(
                    "success"
                )
            ):

                log_action(
                    tool_name=action_request[
                        "tool"
                    ],
                    permission_level=action_request[
                        "permission_level"
                    ],
                    status="blocked",
                    arguments=action_request[
                        "arguments"
                    ]
                )


                answer = (
                    "Sir, that action is blocked by my "
                    "permission policy and cannot be executed."
                )


                brain.store_conversation(
                    question,
                    answer
                )


                print(
                    f"\nJARVIS: {answer}\n"
                )

                continue


            if tool_result.get(
                "success"
            ):

                log_action(
                    tool_name=action_request[
                        "tool"
                    ],
                    permission_level=action_request[
                        "permission_level"
                    ],
                    status="executed",
                    arguments=action_request[
                        "arguments"
                    ]
                )


            else:

                log_action(
                    tool_name=action_request[
                        "tool"
                    ],
                    permission_level=action_request[
                        "permission_level"
                    ],
                    status="failed",
                    arguments=action_request[
                        "arguments"
                    ]
                )


            if action_request[
                "tool"
            ] == "get_system_info":

                answer = format_system_info_response(
                    tool_result
                )


            elif action_request[
                "tool"
            ] == "get_current_datetime":

                answer = format_datetime_response(
                    tool_result
                )


            elif action_request[
                "tool"
            ] == "list_project_directory":

                answer = format_project_directory_response(
                    tool_result
                )


            elif action_request[
                "tool"
            ] == "list_notes":

                answer = format_note_list_response(
                    tool_result
                )


            elif action_request[
                "tool"
            ] == "read_note":

                answer = format_note_read_response(
                    tool_result
                )


            elif action_request[
                "tool"
            ] == "search_notes":

                answer = format_note_search_response(
                    tool_result
                )


            elif action_request[
                "tool"
            ] == "edit_note":

                answer = format_note_edit_response(
                    tool_result
                )


            elif action_request[
                "tool"
            ] == "delete_note":

                answer = format_note_delete_response(
                    tool_result
                )


            elif action_request[
                "tool"
            ] == "list_tasks":

                answer = format_task_list_response(
                    tool_result
                )


            elif action_request[
                "tool"
            ] == "search_tasks":

                answer = format_task_search_response(
                    tool_result
                )


            elif action_request[
                "tool"
            ] == "filter_tasks":

                answer = format_task_filter_response(
                    tool_result
                )


            elif action_request[
                "tool"
            ] == "create_task":

                answer = format_task_creation_response(
                    tool_result
                )


            elif action_request[
                "tool"
            ] == "complete_task":

                answer = format_task_completion_response(
                    tool_result
                )


            elif action_request[
                "tool"
            ] == "delete_task":

                answer = format_task_delete_response(
                    tool_result
                )


            elif action_request[
                "tool"
            ] == "test_confirmed_action":

                answer = format_confirmation_test_response(
                    tool_result
                )


            elif action_request[
                "tool"
            ] == "create_note":

                answer = format_note_creation_response(
                    tool_result
                )


            else:

                answer = (
                    "Sir, the requested tool completed, "
                    "but I do not yet have a response "
                    "formatter configured for it."
                )


            brain.store_conversation(
                question,
                answer
            )


            print(
                f"\nJARVIS: {answer}\n"
            )

            continue


        # note: Prevent ordinary conversational fallback from claiming
        # that an action occurred when no registered Python-controlled
        # action successfully handled the request.
        normalized_fallback_request = " ".join(
            question.lower().strip().split()
        )


        # note: These prefixes represent requests that appear to ask
        # JARVIS to change state or perform an external action. If one
        # reaches conversational fallback, it failed to enter a valid
        # tool-execution path and must therefore fail closed.
        unhandled_action_prefixes = (
            "delete ",
            "remove ",
            "get rid of ",
            "clear ",
            "erase ",
            "send ",
            "email ",
            "write down ",
            "save ",
            "create ",
            "edit ",
            "change ",
            "complete ",
            "mark ",
            "add "
        )


        # note: Vague execution-style follow-ups are also blocked here
        # when no pending action or validated tool handled them earlier.
        vague_action_requests = {
            "can you handle that for me",
            "can you handle that",
            "could you handle that for me",
            "handle that for me",
            "take care of it",
            "take care of that",
            "do it",
            "go ahead",
            "just do it"
        }


        appears_to_request_action = (
            normalized_fallback_request.startswith(
                unhandled_action_prefixes
            )
            or normalized_fallback_request.rstrip(
                "?!. "
            ) in vague_action_requests
        )


        if appears_to_request_action:

            # note: Record unsupported or otherwise unhandled
            # action requests so fail-closed decisions remain
            # visible in JARVIS's audit trail.
            log_action(
                tool_name="unhandled_action_request",
                permission_level="blocked",
                status="blocked",
                arguments={},
                details={
                    "reason": "no_registered_validated_action"
                }
            )


            answer = (
                "Sir, that appears to request an action, but no "
                "registered and validated action reached execution. "
                "I have not performed anything."
            )


            brain.store_conversation(
                question,
                answer
            )


            print(
                f"\nJARVIS: {answer}\n"
            )

            continue


        # note: Select the skill that best matches the user's request.
        selected_skill_name = select_skill(
            question,
            skills
        )


        selected_skill = skills[
            selected_skill_name
        ]


        # note: Restrict knowledge retrieval when the user
        # explicitly names one or more available knowledge domains.
        allowed_domains = select_allowed_domains(
            question,
            knowledge
        )


        # note: Retrieve relevant knowledge chunks while preserving
        # their source, section, domain, and stable chunk identity.
        retrieved = retrieve_knowledge_chunks(
            question,
            knowledge,
            allowed_domains=allowed_domains
        )

        relevant_knowledge = []

        # note: Preserve retrieval metadata so the brain can use
        # source-aware knowledge instead of unlabeled document text.
        for result in retrieved:
            relevant_knowledge.append(
                {
                    "chunk_id": result[
                        "chunk_id"
                    ],
                    "domain": result[
                        "domain"
                    ],
                    # note: Preserve the more specific source group so
                    # nested knowledge organization reaches the brain.
                    "source_group": result[
                        "source_group"
                    ],
                    "filename": result[
                        "filename"
                    ],
                    "document_title": result[
                        "document_title"
                    ],
                    "heading": result[
                        "heading"
                    ],
                    "section_path": result[
                        "section_path"
                    ],
                    "content": result[
                        "content"
                    ]
                }
            )

        # note: Fail closed for knowledge-grounded skills when
        # no trusted local knowledge was retrieved for the request.
        knowledge_grounded_skills = {
            "answer_question",
            "explain"
        }

        if (
            selected_skill_name in knowledge_grounded_skills
            and not relevant_knowledge
        ):
            answer = (
                "I do not have enough information in my available "
                "knowledge to answer that reliably, Sir."
            )

        else:
            # note: Generate the final answer using JARVIS's local brain
            # when trusted knowledge is available or the request does not
            # require knowledge-grounded behavior.
            answer = brain.generate_answer(
                question,
                core_instructions,
                selected_skill,
                relevant_knowledge
            )

        # note: Display JARVIS's final response to the user.
        print(
            f"\nJARVIS: {answer}\n"
        )


# note: Start JARVIS when this file is executed directly.
if __name__ == "__main__":

    main()
