# note: Import the deterministic JARVIS tool-routing system
# and its routing-state constants.
from tools.tool_router import (
    classify_tool_request,
    select_tool,
    ROUTE_MATCHED,
    ROUTE_AMBIGUOUS,
    ROUTE_NO_MATCH
)


# note: Define deterministic routing cases that should map
# directly to registered JARVIS tools.
MATCHED_TESTS = [

    # note: Current date and time routing.
    (
        "What time is it?",
        "get_current_datetime"
    ),
    (
        "Can you tell me the current time right now?",
        "get_current_datetime"
    ),
    (
        "Give me today's date.",
        "get_current_datetime"
    ),
    (
        "What day is it?",
        "get_current_datetime"
    ),

    # note: System-information routing.
    (
        "Show system information.",
        "get_system_info"
    ),
    (
        "What operating system am I using?",
        "get_system_info"
    ),
    (
        "What Python version are you running?",
        "get_system_info"
    ),
    (
        "What architecture is this computer?",
        "get_system_info"
    ),

    # note: Approved JARVIS project-directory routing.
    (
        "What files are in the JARVIS folder?",
        "list_project_directory"
    ),
    (
        "Can you show me the files inside this project?",
        "list_project_directory"
    ),
    (
        "List project files.",
        "list_project_directory"
    ),
    (
        "Show the JARVIS directory.",
        "list_project_directory"
    ),

    # note: Controlled note-creation routing.
    (
        "Create a note that says router test.",
        "create_note"
    ),
    (
        "Make a note saying call the dentist.",
        "create_note"
    ),
    (
        "Write a note to review the logs.",
        "create_note"
    ),
    (
        "Write down that Step 29F live testing has started.",
        "create_note",
    ),
    (
        "Save a note that says Phase 5.",
        "create_note"
    ),

    # note: Step 27A note-listing routing.
    (
        "Show me my notes.",
        "list_notes"
    ),
    (
        "What notes do I have?",
        "list_notes"
    ),
    (
        "List my notes.",
        "list_notes"
    ),
    (
        "Show notes.",
        "list_notes"
    ),
    (
        "What notes are saved?",
        "list_notes"
    ),
    (
        "List saved notes.",
        "list_notes"
    ),

    # note: Step 27B explicit note-reading routing.
    (
        "Read note_20260831_204753_209576.txt",
        "read_note"
    ),
    (
        "Open note_20260831_204753_209576.txt",
        "read_note"
    ),
    (
        "Show me note_20260831_204753_209576.txt",
        "read_note"
    ),
    (
        "Please read note_20260831_204753_209576.txt",
        "read_note"
    ),
    (
        "Please open note_20260831_204753_209576.txt",
        "read_note"
    ),

    # note: Step 27C deterministic note-search routing.
    (
        "Search my notes for audit",
        "search_notes"
    ),
    (
        "Find notes containing router",
        "search_notes"
    ),
    (
        "Which notes mention Phase 5?",
        "search_notes"
    ),
    (
        "What notes contain audit?",
        "search_notes"
    ),
    (
        "Please search my notes for audit logs",
        "search_notes"
    ),

    # note: Step 27D deterministic note-edit routing requires
    # both an exact JARVIS note filename and replacement content.
    (
        (
            "Edit note_20260901_172531_472475.txt "
            "to say review the new audit logs."
        ),
        "edit_note"
    ),
    (
        (
            "Update note_20260901_172531_472475.txt "
            "to read Phase 5 is complete."
        ),
        "edit_note"
    ),
    (
        (
            "Please change note_20260901_172531_472475.txt "
            "to contain updated content."
        ),
        "edit_note"
    ),
    (
        (
            'Edit "note_20260901_172531_472475.txt" '
            'to say "quoted content."'
        ),
        "edit_note"
    ),

    # note: Step 27E deterministic note deletion requires
    # one exact JARVIS-generated note filename.
    (
        "Delete note_20260901_172531_472475.txt",
        "delete_note"
    ),
    (
        "Remove note_20260901_172531_472475.txt",
        "delete_note"
    ),
    (
        "Please delete note_20260901_172531_472475.txt",
        "delete_note"
    ),
    (
        'Delete "note_20260901_172531_472475.txt"',
        "delete_note"
    ),

    # note: Step 28G deterministic task creation routing.
    (
        "Create a task to review the audit logs.",
        "create_task"
    ),
    (
        "Add a task to finish the router tests.",
        "create_task"
    ),

    # note: Step 28G deterministic task-listing routing.
    (
        "Show my tasks.",
        "list_tasks"
    ),
    (
        "List my tasks.",
        "list_tasks"
    ),

    # note: Step 28G deterministic task-search routing.
    (
        "Search my tasks for audit.",
        "search_tasks"
    ),
    (
        "Find tasks containing router.",
        "search_tasks"
    ),

    # note: Step 28G deterministic task-status filtering.
    (
        "Show my open tasks.",
        "filter_tasks"
    ),
    (
        "Show my completed tasks.",
        "filter_tasks"
    ),

    # note: Step 28G task completion requires one exact
    # positive numeric task ID.
    (
        "Complete task 3.",
        "complete_task"
    ),
    (
        "Mark task 4 complete.",
        "complete_task"
    ),
    (
        "Mark task 5 as completed.",
        "complete_task"
    ),

    # note: Step 28G task deletion requires one exact
    # positive numeric task ID.
    (
        "Delete task 6.",
        "delete_task"
    ),
    (
        "Remove task 7.",
        "delete_task"
    ),

    # note: Permission-system test routing.
    (
        "Perform the test action.",
        "test_confirmed_action"
    ),
    (
        "Run the confirmation test.",
        "test_confirmed_action"
    ),
    (
        "Perform the blocked action.",
        "test_blocked_action"
    ),
    (
        "Run the blocked test.",
        "test_blocked_action"
    ),

    # note: Unsupported filesystem requests must be intercepted
    # before they can reach the language model.
    (
        "Show me the files in my Desktop folder.",
        "filesystem_access_denied"
    ),
    (
        "List the files in Downloads.",
        "filesystem_access_denied"
    ),
    (
        "Read ../../Desktop/test.txt",
        "filesystem_access_denied"
    ),
    (
        "Read /etc/passwd",
        "filesystem_access_denied"
    ),
    (
        "Open /var/log/system.log",
        "filesystem_access_denied"
    ),

    # note: Step 27E destructive filesystem requests must also
    # be denied deterministically instead of reaching the LLM.
    (
        "Delete ../../Desktop/test.txt",
        "filesystem_access_denied"
    ),
    (
        "Delete /etc/passwd",
        "filesystem_access_denied"
    ),
    (
        "Delete ordinary_file.txt",
        "filesystem_access_denied"
    )
]


# note: Define requests that intentionally lack enough information
# for JARVIS to choose a safe tool.
AMBIGUOUS_TESTS = [

    # note: Step 27B ambiguous note-reading requests.
    (
        "Open note.",
        "ambiguous_note_request"
    ),
    (
        "Read note.",
        "ambiguous_note_request"
    ),
    (
        "Open a note.",
        "ambiguous_note_request"
    ),
    (
        "Read a note.",
        "ambiguous_note_request"
    ),
    (
        "Show me a note.",
        "ambiguous_note_request"
    ),
    (
        "My note.",
        "ambiguous_note_request"
    ),
    (
        "The note.",
        "ambiguous_note_request"
    ),

    # note: Step 25 ambiguous project requests.
    (
        "Show me the project.",
        "ambiguous_project_request"
    ),
    (
        "Open project.",
        "ambiguous_project_request"
    ),
    (
        "Show me JARVIS.",
        "ambiguous_project_request"
    ),

    # note: Step 27C incomplete note-search requests must stop
    # before reaching the language model.
    (
        "Search my notes for",
        "ambiguous_note_search_request"
    ),
    (
        "Find notes containing",
        "ambiguous_note_search_request"
    ),

    # note: Step 27D incomplete note-edit requests must stop
    # before reaching the language model or guessing a write.
    (
        "Edit my note.",
        "ambiguous_note_edit_request"
    ),
    (
        "Change the note about audit.",
        "ambiguous_note_edit_request"
    ),
    (
        "Update a note.",
        "ambiguous_note_edit_request"
    ),
    (
        "Edit note_20260901_172531_472475.txt",
        "ambiguous_note_edit_request"
    ),

    # note: Step 27E vague, descriptive, and bulk deletion
    # requests must never cause JARVIS to guess a target.
    (
        "Delete my note.",
        "ambiguous_note_delete_request"
    ),
    (
        "Delete the audit note.",
        "ambiguous_note_delete_request"
    ),
    (
        "Remove a note.",
        "ambiguous_note_delete_request"
    ),
    (
        "Delete all my notes.",
        "ambiguous_note_delete_request"
    ),

    # note: Step 28G incomplete task creation must not
    # manufacture a title.
    (
        "Create a task.",
        "ambiguous_task_creation_request"
    ),

    # note: Step 28G incomplete task search must not
    # manufacture a query.
    (
        "Search my tasks.",
        "ambiguous_task_search_request"
    ),

    # note: Unsupported task states remain ambiguous rather
    # than being silently converted to open/completed.
    (
        "Show my pending tasks.",
        "unsupported_task_status_filter"
    ),

    # note: Task completion must never guess an ID from a
    # vague or descriptive task reference.
    (
        "Complete a task.",
        "ambiguous_task_completion_request"
    ),
    (
        "Complete the audit task.",
        "ambiguous_task_completion_request"
    ),
    (
        "Mark the router task complete.",
        "ambiguous_task_completion_request"
    ),

    # note: Task deletion must never guess an ID from a
    # vague or descriptive task reference.
    (
        "Delete my task.",
        "ambiguous_task_delete_request"
    ),
    (
        "Delete the audit task.",
        "ambiguous_task_delete_request"
    ),
    (
        "Remove a task.",
        "ambiguous_task_delete_request"
    ),

    # note: A bare task reference cannot safely select among
    # listing, searching, filtering, completion, or deletion.
    (
        "Tasks.",
        "ambiguous_task_request"
    )
]


# note: Define ordinary conversational requests that should
# remain available to JARVIS's normal reasoning path.
NO_MATCH_TESTS = [

    "What is my favorite color?",
    "Change my favorite color to green.",
    "Explain governance.",
    "Tell me about Perform.",
    "What are the four GRC capabilities?",
    "How are you today?"
]


# note: Track test totals so failures are visible and the
# script can return a failing process exit code.
passed = 0
failed = 0


print(
    "\nJARVIS Tool Router Tests\n"
)


# note: Verify every clear request produces the expected tool
# and reports a matched routing state.
print(
    "Matched Routing Tests\n"
)


for index, (
    request,
    expected_tool
) in enumerate(
    MATCHED_TESTS,
    start=1
):

    result = classify_tool_request(
        request
    )


    actual_status = result.get(
        "status"
    )

    actual_tool = result.get(
        "tool"
    )


    selected_tool = select_tool(
        request
    )


    test_passed = (
        actual_status == ROUTE_MATCHED
        and actual_tool == expected_tool
        and selected_tool == expected_tool
    )


    if test_passed:

        passed += 1

        print(
            f"[PASS] {index:02d} | "
            f"{request}"
        )


    else:

        failed += 1

        print(
            f"[FAIL] {index:02d} | "
            f"{request}"
        )

        print(
            f"       Expected status: {ROUTE_MATCHED}"
        )

        print(
            f"       Actual status:   {actual_status}"
        )

        print(
            f"       Expected tool:   {expected_tool}"
        )

        print(
            f"       Actual tool:     {actual_tool}"
        )

        print(
            f"       select_tool():   {selected_tool}"
        )


# note: Verify vague requests are stopped as ambiguous rather
# than being routed to a tool or silently passed to the LLM.
print(
    "\nAmbiguous Routing Tests\n"
)


for index, (
    request,
    expected_reason
) in enumerate(
    AMBIGUOUS_TESTS,
    start=1
):

    result = classify_tool_request(
        request
    )


    actual_status = result.get(
        "status"
    )

    actual_tool = result.get(
        "tool"
    )

    actual_reason = result.get(
        "reason"
    )


    selected_tool = select_tool(
        request
    )


    test_passed = (
        actual_status == ROUTE_AMBIGUOUS
        and actual_tool is None
        and actual_reason == expected_reason
        and selected_tool is None
    )


    if test_passed:

        passed += 1

        print(
            f"[PASS] {index:02d} | "
            f"{request}"
        )


    else:

        failed += 1

        print(
            f"[FAIL] {index:02d} | "
            f"{request}"
        )

        print(
            f"       Expected status: {ROUTE_AMBIGUOUS}"
        )

        print(
            f"       Actual status:   {actual_status}"
        )

        print(
            f"       Expected reason: {expected_reason}"
        )

        print(
            f"       Actual reason:   {actual_reason}"
        )

        print(
            f"       Actual tool:     {actual_tool}"
        )

        print(
            f"       select_tool():   {selected_tool}"
        )


# note: Verify unrelated requests remain available to the
# normal skill, knowledge, memory, or language-model path.
print(
    "\nNo-Match Routing Tests\n"
)


for index, request in enumerate(
    NO_MATCH_TESTS,
    start=1
):

    result = classify_tool_request(
        request
    )


    actual_status = result.get(
        "status"
    )

    actual_tool = result.get(
        "tool"
    )


    selected_tool = select_tool(
        request
    )


    test_passed = (
        actual_status == ROUTE_NO_MATCH
        and actual_tool is None
        and selected_tool is None
    )


    if test_passed:

        passed += 1

        print(
            f"[PASS] {index:02d} | "
            f"{request}"
        )


    else:

        failed += 1

        print(
            f"[FAIL] {index:02d} | "
            f"{request}"
        )

        print(
            f"       Expected status: {ROUTE_NO_MATCH}"
        )

        print(
            f"       Actual status:   {actual_status}"
        )

        print(
            f"       Actual tool:     {actual_tool}"
        )

        print(
            f"       select_tool():   {selected_tool}"
        )


# note: Print a final regression-test summary.
total = (
    passed
    + failed
)


print(
    "\n------------------------------"
)

print(
    f"Passed: {passed}"
)

print(
    f"Failed: {failed}"
)

print(
    f"Total:  {total}"
)

print(
    "------------------------------\n"
)


# note: Return a nonzero process status when any routing
# regression has been detected.
if failed:

    raise SystemExit(
        1
    )
