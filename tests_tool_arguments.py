# note: Import the deterministic JARVIS tool-argument
# extraction, validation, and preparation functions.
from tools.tool_arguments import (
    extract_note_content,
    extract_note_filename,
    extract_note_search_query,
    extract_note_edit_arguments,
    extract_note_delete_filename,
    extract_task_create_arguments,
    extract_task_search_query,
    extract_task_filter_status,
    extract_complete_task_id,
    extract_delete_task_id,
    extract_tool_arguments,
    validate_tool_arguments,
    prepare_tool_arguments
)


# note: Track total successful and failed regression tests.
passed = 0
failed = 0


# note: Provide one small helper for consistent PASS/FAIL
# output throughout the argument test suite.
def report_test(
    name,
    condition,
    details=None
):

    """Report one automated regression-test result."""

    global passed
    global failed

    if condition:

        passed += 1

        print(
            f"[PASS] {name}"
        )

    else:

        failed += 1

        print(
            f"[FAIL] {name}"
        )

        if details is not None:

            print(
                f"       {details}"
            )


print(
    "\nNote Argument Extraction Tests\n"
)


# note: Verify the original Step 26 note-content extraction
# behavior continues working, including natural write-down
# phrasing discovered during Step 29F live testing.
NOTE_CONTENT_TESTS = [
    (
        "Create a note that says buy milk.",
        "buy milk."
    ),
    (
        "Make a note saying call the dentist.",
        "call the dentist."
    ),
    (
        "Write a note to check the logs.",
        "check the logs."
    ),
    (
        "Save a note that says router test.",
        "router test."
    ),
    (
        "Please create a note that says review Phase 5 tomorrow.",
        "review Phase 5 tomorrow."
    ),
    (
        (
            "Please save a note for me reminding me "
            "to review the audit logs."
        ),
        "review the audit logs."
    ),
    (
        "Write down that Step 29F live testing has started.",
        "Step 29F live testing has started."
    )
]

for index, (
    request,
    expected
) in enumerate(
    NOTE_CONTENT_TESTS,
    start=1
):

    actual = extract_note_content(
        request
    )

    report_test(
        f"{index:02d} | {request}",
        actual == expected,
        (
            f"Expected {expected!r}, "
            f"received {actual!r}"
        )
    )


# note: Verify Step 27B filename extraction preserves the
# complete JARVIS note filename, including the note_ prefix.
print(
    "\nNote Filename Extraction Tests\n"
)


NOTE_FILENAME = (
    "note_20260831_204753_209576.txt"
)

NOTE_EDIT_FILENAME = (
    "note_20260901_172531_472475.txt"
)

NOTE_DELETE_FILENAME = (
    "note_20260902_105121_364018.txt"
)


NOTE_FILENAME_TESTS = [
    (
        f"Read {NOTE_FILENAME}",
        NOTE_FILENAME
    ),
    (
        f"Open {NOTE_FILENAME}",
        NOTE_FILENAME
    ),
    (
        f"Show me {NOTE_FILENAME}",
        NOTE_FILENAME
    ),
    (
        f"Please read {NOTE_FILENAME}",
        NOTE_FILENAME
    ),
    (
        f"Please open {NOTE_FILENAME}",
        NOTE_FILENAME
    ),
    (
        f'Read "{NOTE_FILENAME}"',
        NOTE_FILENAME
    )
]


for index, (
    request,
    expected
) in enumerate(
    NOTE_FILENAME_TESTS,
    start=1
):

    actual = extract_note_filename(
        request
    )

    report_test(
        f"{index:02d} | {request}",
        actual == expected,
        (
            f"Expected {expected!r}, "
            f"received {actual!r}"
        )
    )


# note: Verify vague note-reading commands do not magically
# produce a filename.
VAGUE_FILENAME_TESTS = [
    "Open note.",
    "Read note.",
    "Open a note.",
    "Read a note."
]


for index, request in enumerate(
    VAGUE_FILENAME_TESTS,
    start=1
):

    actual = extract_note_filename(
        request
    )

    report_test(
        f"Vague {index:02d} | {request}",
        actual is None,
        (
            f"Expected None, received {actual!r}"
        )
    )


# note: Verify Step 27C deterministic note-search query
# extraction for supported natural-language search requests.
print(
    "\nNote Search Query Extraction Tests\n"
)


NOTE_SEARCH_QUERY_TESTS = [
    (
        "Search my notes for audit",
        "audit"
    ),
    (
        "Find notes containing router",
        "router"
    ),
    (
        "Which notes mention Phase 5?",
        "Phase 5"
    ),
    (
        'Search my notes for "audit logs"',
        "audit logs"
    )
]


for index, (
    request,
    expected
) in enumerate(
    NOTE_SEARCH_QUERY_TESTS,
    start=1
):

    actual = extract_note_search_query(
        request
    )

    report_test(
        f"{index:02d} | {request}",
        actual == expected,
        (
            f"Expected {expected!r}, "
            f"received {actual!r}"
        )
    )


# note: Verify an incomplete note-search request does not
# manufacture a search query.
actual = extract_note_search_query(
    "Search my notes for "
)

report_test(
    "Incomplete note-search query",
    actual is None,
    (
        f"Expected None, received {actual!r}"
    )
)


# note: Verify Step 27D extracts both the exact filename and
# full replacement content from supported edit commands.
print(
    "\nNote Edit Argument Extraction Tests\n"
)


NOTE_EDIT_EXTRACTION_TESTS = [
    (
        (
            f"Edit {NOTE_EDIT_FILENAME} "
            "to say review the new audit logs."
        ),
        {
            "filename": NOTE_EDIT_FILENAME,
            "content": "review the new audit logs."
        }
    ),
    (
        (
            f"Update {NOTE_EDIT_FILENAME} "
            "to read Phase 5 is complete."
        ),
        {
            "filename": NOTE_EDIT_FILENAME,
            "content": "Phase 5 is complete."
        }
    ),
    (
        (
            f"Please change {NOTE_EDIT_FILENAME} "
            "to contain updated content."
        ),
        {
            "filename": NOTE_EDIT_FILENAME,
            "content": "updated content."
        }
    ),
    (
        (
            f'Edit "{NOTE_EDIT_FILENAME}" '
            'to say "quoted replacement content."'
        ),
        {
            "filename": NOTE_EDIT_FILENAME,
            "content": "quoted replacement content."
        }
    )
]


for index, (
    request,
    expected
) in enumerate(
    NOTE_EDIT_EXTRACTION_TESTS,
    start=1
):

    actual = extract_note_edit_arguments(
        request
    )

    report_test(
        f"Edit extraction {index:02d} | {request}",
        actual == expected,
        (
            f"Expected {expected!r}, "
            f"received {actual!r}"
        )
    )


# note: Verify incomplete edit commands do not manufacture
# either a filename or replacement content.
INCOMPLETE_NOTE_EDIT_TESTS = [
    "Edit my note.",
    f"Edit {NOTE_EDIT_FILENAME}"
]


for index, request in enumerate(
    INCOMPLETE_NOTE_EDIT_TESTS,
    start=1
):

    actual = extract_note_edit_arguments(
        request
    )

    report_test(
        f"Incomplete edit {index:02d} | {request}",
        actual is None,
        (
            f"Expected None, received {actual!r}"
        )
    )


# note: Verify Step 27E extracts exact deletion targets while
# refusing vague or bulk note references.
print(
    "\nNote Delete Filename Extraction Tests\n"
)


NOTE_DELETE_EXTRACTION_TESTS = [
    (
        f"Delete {NOTE_DELETE_FILENAME}",
        NOTE_DELETE_FILENAME
    ),
    (
        f"Remove {NOTE_DELETE_FILENAME}",
        NOTE_DELETE_FILENAME
    ),
    (
        f"Please delete {NOTE_DELETE_FILENAME}",
        NOTE_DELETE_FILENAME
    ),
    (
        f'Delete "{NOTE_DELETE_FILENAME}"',
        NOTE_DELETE_FILENAME
    ),
    (
        "Delete my note.",
        None
    ),
    (
        "Delete all my notes.",
        None
    )
]


for index, (
    request,
    expected
) in enumerate(
    NOTE_DELETE_EXTRACTION_TESTS,
    start=1
):

    actual = extract_note_delete_filename(
        request
    )

    report_test(
        f"Delete extraction {index:02d} | {request}",
        actual == expected,
        (
            f"Expected {expected!r}, "
            f"received {actual!r}"
        )
    )


# note: A descriptive target may be extracted as text, but it
# must never become a valid JARVIS note deletion argument.
actual = extract_note_delete_filename(
    "Delete the audit note."
)

report_test(
    "Descriptive delete target remains non-executable",
    actual == "the audit note",
    (
        "Expected the extractor to preserve the supplied "
        f"description, received {actual!r}"
    )
)


# note: Step 28G verifies deterministic extraction for task
# creation, including optional strict due-date text.
print(
    "\nTask Create Argument Extraction Tests\n"
)


TASK_CREATE_EXTRACTION_TESTS = [
    (
        "Create a task to review the audit logs.",
        {
            "title": "review the audit logs"
        }
    ),
    (
        "Add a task to finish the router tests.",
        {
            "title": "finish the router tests"
        }
    ),
    (
        "Please create a task to call the dentist.",
        {
            "title": "call the dentist"
        }
    ),
    (
        "Create a task to finish the report due 2026-09-10.",
        {
            "title": "finish the report",
            "due_date": "2026-09-10"
        }
    ),
    (
        "Add a task to review controls due 2026-12-31",
        {
            "title": "review controls",
            "due_date": "2026-12-31"
        }
    )
]


for index, (
    request,
    expected
) in enumerate(
    TASK_CREATE_EXTRACTION_TESTS,
    start=1
):

    actual = extract_task_create_arguments(
        request
    )

    report_test(
        f"Task create extraction {index:02d} | {request}",
        actual == expected,
        (
            f"Expected {expected!r}, "
            f"received {actual!r}"
        )
    )


# note: Incomplete task creation must not manufacture a title.
TASK_CREATE_INCOMPLETE_TESTS = [
    "Create a task.",
    "Add a task.",
    "Please create a task.",
    "Please add a task."
]


for index, request in enumerate(
    TASK_CREATE_INCOMPLETE_TESTS,
    start=1
):

    actual = extract_task_create_arguments(
        request
    )

    report_test(
        f"Incomplete task create {index:02d} | {request}",
        actual is None,
        (
            f"Expected None, received {actual!r}"
        )
    )


# note: Step 28G verifies deterministic task-search extraction
# and conversational punctuation cleanup.
print(
    "\nTask Search Query Extraction Tests\n"
)


# note: Verify deterministic task-search extraction, including
# natural singular-task wording discovered during Step 29F.
TASK_SEARCH_EXTRACTION_TESTS = [
    (
        "Search my tasks for audit.",
        "audit"
    ),
    (
        "Find tasks containing router.",
        "router"
    ),
    (
        "Which tasks mention Phase 5?",
        "Phase 5"
    ),
    (
        'Search my tasks for "audit logs"',
        "audit logs"
    ),
    (
        "Can you find the task where I mentioned audit logs?",
        "audit logs"
    )
]

for index, (
    request,
    expected
) in enumerate(
    TASK_SEARCH_EXTRACTION_TESTS,
    start=1
):

    actual = extract_task_search_query(
        request
    )

    report_test(
        f"Task search extraction {index:02d} | {request}",
        actual == expected,
        (
            f"Expected {expected!r}, "
            f"received {actual!r}"
        )
    )


# note: Incomplete task searches must never create a query.
actual = extract_task_search_query(
    "Search my tasks."
)

report_test(
    "Incomplete task-search query",
    actual is None,
    (
        f"Expected None, received {actual!r}"
    )
)


# note: Step 28G status extraction accepts only the two
# supported local task states.
print(
    "\nTask Status Extraction Tests\n"
)


TASK_STATUS_EXTRACTION_TESTS = [
    (
        "Show my open tasks.",
        "open"
    ),
    (
        "List open tasks.",
        "open"
    ),
    (
        "Which tasks are open?",
        "open"
    ),
    (
        "Show my completed tasks.",
        "completed"
    ),
    (
        "List completed tasks.",
        "completed"
    ),
    (
        "Which tasks are completed?",
        "completed"
    ),
    (
        "Show my pending tasks.",
        None
    )
]


for index, (
    request,
    expected
) in enumerate(
    TASK_STATUS_EXTRACTION_TESTS,
    start=1
):

    actual = extract_task_filter_status(
        request
    )

    report_test(
        f"Task status extraction {index:02d} | {request}",
        actual == expected,
        (
            f"Expected {expected!r}, "
            f"received {actual!r}"
        )
    )


# note: Step 28G completion extraction accepts only one exact
# positive numeric task ID.
print(
    "\nTask Completion ID Extraction Tests\n"
)


TASK_COMPLETION_ID_TESTS = [
    (
        "Complete task 3.",
        3
    ),
    (
        "Mark task 4 complete.",
        4
    ),
    (
        "Mark task 5 as completed.",
        5
    ),
    (
        "Please complete task 12.",
        12
    ),
    (
        "Complete a task.",
        None
    ),
    (
        "Complete the audit task.",
        None
    ),
    (
        "Complete task zero.",
        None
    ),
    (
        "Complete task 0.",
        None
    )
]


for index, (
    request,
    expected
) in enumerate(
    TASK_COMPLETION_ID_TESTS,
    start=1
):

    actual = extract_complete_task_id(
        request
    )

    report_test(
        f"Task completion extraction {index:02d} | {request}",
        actual == expected,
        (
            f"Expected {expected!r}, "
            f"received {actual!r}"
        )
    )


# note: Step 28G deletion extraction accepts only one exact
# positive numeric task ID.
print(
    "\nTask Delete ID Extraction Tests\n"
)


TASK_DELETE_ID_TESTS = [
    (
        "Delete task 5.",
        5
    ),
    (
        "Remove task 6.",
        6
    ),
    (
        "Please delete task 10.",
        10
    ),
    (
        "Please remove task 11.",
        11
    ),
    (
        "Delete my task.",
        None
    ),
    (
        "Delete the audit task.",
        None
    ),
    (
        "Delete task zero.",
        None
    ),
    (
        "Delete task 0.",
        None
    )
]


for index, (
    request,
    expected
) in enumerate(
    TASK_DELETE_ID_TESTS,
    start=1
):

    actual = extract_delete_task_id(
        request
    )

    report_test(
        f"Task delete extraction {index:02d} | {request}",
        actual == expected,
        (
            f"Expected {expected!r}, "
            f"received {actual!r}"
        )
    )


print(
    "\nTool Argument Validation Tests\n"
)


# note: Verify valid controlled note-writing content.
result = validate_tool_arguments(
    "create_note",
    {
        "content": "review the logs"
    }
)

report_test(
    "Valid note content",
    result.get(
        "valid"
    ) is True,
    result
)


# note: Verify missing note content fails closed.
result = validate_tool_arguments(
    "create_note",
    {}
)

report_test(
    "Missing note content",
    result.get(
        "valid"
    ) is False,
    result
)


# note: Verify blank note content fails validation.
result = validate_tool_arguments(
    "create_note",
    {
        "content": "   "
    }
)

report_test(
    "Empty note content",
    result.get(
        "valid"
    ) is False,
    result
)


# note: Verify non-string note content fails validation.
result = validate_tool_arguments(
    "create_note",
    {
        "content": 123
    }
)

report_test(
    "Wrong note content type",
    result.get(
        "valid"
    ) is False,
    result
)


# note: Verify unexpected arguments are rejected.
result = validate_tool_arguments(
    "create_note",
    {
        "content": "test",
        "path": "/tmp/test.txt"
    }
)

report_test(
    "Unexpected argument",
    result.get(
        "valid"
    ) is False,
    result
)


# note: Verify a no-argument safe-read tool accepts an
# empty argument dictionary.
result = validate_tool_arguments(
    "get_current_datetime",
    {}
)

report_test(
    "No-argument time tool",
    result.get(
        "valid"
    ) is True,
    result
)


# note: Verify arguments cannot be injected into a
# no-argument safe-read tool.
result = validate_tool_arguments(
    "get_current_datetime",
    {
        "timezone": "UTC"
    }
)

report_test(
    "Unexpected time argument",
    result.get(
        "valid"
    ) is False,
    result
)


# note: Verify Step 27A list_notes remains a true
# zero-argument tool.
result = validate_tool_arguments(
    "list_notes",
    {}
)

report_test(
    "No-argument list_notes tool",
    result.get(
        "valid"
    ) is True,
    result
)


result = validate_tool_arguments(
    "list_notes",
    {
        "path": "../"
    }
)

report_test(
    "Reject list_notes path injection",
    result.get(
        "valid"
    ) is False,
    result
)


# note: Verify a proper generated JARVIS note filename
# passes Step 27B argument validation.
result = validate_tool_arguments(
    "read_note",
    {
        "filename": NOTE_FILENAME
    }
)

report_test(
    "Valid read_note filename",
    result.get(
        "valid"
    ) is True,
    result
)


# note: Verify the read tool rejects path traversal.
result = validate_tool_arguments(
    "read_note",
    {
        "filename": "../../Desktop/test.txt"
    }
)

report_test(
    "Reject read_note path traversal",
    result.get(
        "valid"
    ) is False,
    result
)


# note: Verify absolute filesystem paths cannot reach
# the controlled note-reading tool.
result = validate_tool_arguments(
    "read_note",
    {
        "filename": "/etc/passwd"
    }
)

report_test(
    "Reject absolute read path",
    result.get(
        "valid"
    ) is False,
    result
)


# note: Verify ordinary text files that are not recognized
# JARVIS-generated notes cannot be supplied to read_note.
result = validate_tool_arguments(
    "read_note",
    {
        "filename": "not_a_note.txt"
    }
)

report_test(
    "Reject non-JARVIS note filename",
    result.get(
        "valid"
    ) is False,
    result
)


# note: Verify files without the required text extension
# cannot be supplied to read_note.
result = validate_tool_arguments(
    "read_note",
    {
        "filename": "note_20260831_204753_209576.json"
    }
)

report_test(
    "Reject non-text note",
    result.get(
        "valid"
    ) is False,
    result
)


# note: Verify read_note requires a filename argument.
result = validate_tool_arguments(
    "read_note",
    {}
)

report_test(
    "Missing read_note filename",
    result.get(
        "valid"
    ) is False,
    result
)


# note: Verify Step 27C accepts a normal plain-text
# search query.
result = validate_tool_arguments(
    "search_notes",
    {
        "query": "audit"
    }
)

report_test(
    "Valid search_notes query",
    result.get(
        "valid"
    ) is True,
    result
)


# note: Verify search_notes requires its query argument.
result = validate_tool_arguments(
    "search_notes",
    {}
)

report_test(
    "Missing search_notes query",
    result.get(
        "valid"
    ) is False,
    result
)


# note: Verify an empty search term cannot reach the
# note-search tool.
result = validate_tool_arguments(
    "search_notes",
    {
        "query": ""
    }
)

report_test(
    "Reject empty search_notes query",
    result.get(
        "valid"
    ) is False,
    result
)


# note: Verify whitespace-only searches fail closed.
result = validate_tool_arguments(
    "search_notes",
    {
        "query": "   "
    }
)

report_test(
    "Reject blank search_notes query",
    result.get(
        "valid"
    ) is False,
    result
)


# note: Verify note-search queries must be text.
result = validate_tool_arguments(
    "search_notes",
    {
        "query": 123
    }
)

report_test(
    "Reject non-string search_notes query",
    result.get(
        "valid"
    ) is False,
    result
)


# note: Verify unexpectedly large search terms are rejected
# by the bounded Step 27C argument policy.
result = validate_tool_arguments(
    "search_notes",
    {
        "query": "a" * 201
    }
)

report_test(
    "Reject oversized search_notes query",
    result.get(
        "valid"
    ) is False,
    result
)


# note: Verify filesystem or other unrelated arguments cannot
# be injected alongside a note-search query.
result = validate_tool_arguments(
    "search_notes",
    {
        "query": "audit",
        "path": "../"
    }
)

report_test(
    "Reject unexpected search_notes argument",
    result.get(
        "valid"
    ) is False,
    result
)


# note: Verify Step 27D accepts an exact generated JARVIS note
# filename together with valid replacement content.
result = validate_tool_arguments(
    "edit_note",
    {
        "filename": NOTE_EDIT_FILENAME,
        "content": "updated content"
    }
)

report_test(
    "Valid edit_note arguments",
    result.get(
        "valid"
    ) is True,
    result
)


# note: Verify edit_note requires the exact note filename.
result = validate_tool_arguments(
    "edit_note",
    {
        "content": "updated content"
    }
)

report_test(
    "Missing edit_note filename",
    result.get(
        "valid"
    ) is False,
    result
)


# note: Verify edit_note requires replacement content.
result = validate_tool_arguments(
    "edit_note",
    {
        "filename": NOTE_EDIT_FILENAME
    }
)

report_test(
    "Missing edit_note content",
    result.get(
        "valid"
    ) is False,
    result
)


# note: Verify edit_note rejects path traversal before
# any filesystem write can be attempted.
result = validate_tool_arguments(
    "edit_note",
    {
        "filename": "../../Desktop/test.txt",
        "content": "changed"
    }
)

report_test(
    "Reject edit_note path traversal",
    result.get(
        "valid"
    ) is False,
    result
)


# note: Verify ordinary text files cannot be supplied to
# the controlled JARVIS note-editing tool.
result = validate_tool_arguments(
    "edit_note",
    {
        "filename": "ordinary_file.txt",
        "content": "changed"
    }
)

report_test(
    "Reject non-JARVIS edit filename",
    result.get(
        "valid"
    ) is False,
    result
)


# note: Verify non-text files cannot reach edit_note.
result = validate_tool_arguments(
    "edit_note",
    {
        "filename": "note_test.json",
        "content": "changed"
    }
)

report_test(
    "Reject non-text edit filename",
    result.get(
        "valid"
    ) is False,
    result
)


# note: Verify blank replacement content cannot erase a note
# through an accidental or incomplete edit request.
result = validate_tool_arguments(
    "edit_note",
    {
        "filename": NOTE_EDIT_FILENAME,
        "content": "   "
    }
)

report_test(
    "Reject blank edit_note content",
    result.get(
        "valid"
    ) is False,
    result
)


# note: Verify replacement content must be text.
result = validate_tool_arguments(
    "edit_note",
    {
        "filename": NOTE_EDIT_FILENAME,
        "content": 123
    }
)

report_test(
    "Reject non-string edit_note content",
    result.get(
        "valid"
    ) is False,
    result
)


# note: Verify the bounded edit policy rejects unexpectedly
# large replacement payloads.
result = validate_tool_arguments(
    "edit_note",
    {
        "filename": NOTE_EDIT_FILENAME,
        "content": "a" * 10001
    }
)

report_test(
    "Reject oversized edit_note content",
    result.get(
        "valid"
    ) is False,
    result
)


# note: Verify unrelated filesystem arguments cannot be
# injected into edit_note.
result = validate_tool_arguments(
    "edit_note",
    {
        "filename": NOTE_EDIT_FILENAME,
        "content": "updated",
        "path": "../"
    }
)

report_test(
    "Reject unexpected edit_note argument",
    result.get(
        "valid"
    ) is False,
    result
)


# note: Verify Step 27E accepts one exact generated
# JARVIS note filename as a deletion target.
result = validate_tool_arguments(
    "delete_note",
    {
        "filename": NOTE_DELETE_FILENAME
    }
)

report_test(
    "Valid delete_note filename",
    result.get(
        "valid"
    ) is True,
    result
)


# note: Verify delete_note requires an exact filename.
result = validate_tool_arguments(
    "delete_note",
    {}
)

report_test(
    "Missing delete_note filename",
    result.get(
        "valid"
    ) is False,
    result
)


# note: Verify path traversal cannot reach the destructive
# JARVIS note-deletion tool.
result = validate_tool_arguments(
    "delete_note",
    {
        "filename": "../../Desktop/test.txt"
    }
)

report_test(
    "Reject delete_note path traversal",
    result.get(
        "valid"
    ) is False,
    result
)


# note: Verify absolute filesystem targets cannot be supplied
# to the note-deletion tool.
result = validate_tool_arguments(
    "delete_note",
    {
        "filename": "/etc/passwd"
    }
)

report_test(
    "Reject absolute delete path",
    result.get(
        "valid"
    ) is False,
    result
)


# note: Verify ordinary text files cannot become JARVIS note
# deletion targets.
result = validate_tool_arguments(
    "delete_note",
    {
        "filename": "ordinary_file.txt"
    }
)

report_test(
    "Reject non-JARVIS delete filename",
    result.get(
        "valid"
    ) is False,
    result
)


# note: Verify non-text files cannot reach delete_note.
result = validate_tool_arguments(
    "delete_note",
    {
        "filename": "note_test.json"
    }
)

report_test(
    "Reject non-text delete filename",
    result.get(
        "valid"
    ) is False,
    result
)


# note: Verify deletion filenames must be text.
result = validate_tool_arguments(
    "delete_note",
    {
        "filename": 123
    }
)

report_test(
    "Reject non-string delete filename",
    result.get(
        "valid"
    ) is False,
    result
)


# note: Verify unrelated arguments cannot be injected into a
# destructive delete_note request.
result = validate_tool_arguments(
    "delete_note",
    {
        "filename": NOTE_DELETE_FILENAME,
        "path": "../"
    }
)

report_test(
    "Reject unexpected delete_note argument",
    result.get(
        "valid"
    ) is False,
    result
)


# note: Step 28G verifies a normal task title is accepted.
result = validate_tool_arguments(
    "create_task",
    {
        "title": "review the audit logs"
    }
)

report_test(
    "Valid create_task title",
    result.get(
        "valid"
    ) is True,
    result
)


# note: Verify a strict supported due date is accepted.
result = validate_tool_arguments(
    "create_task",
    {
        "title": "finish report",
        "due_date": "2026-09-10"
    }
)

report_test(
    "Valid create_task due date",
    result.get(
        "valid"
    ) is True,
    result
)


# note: Task creation requires a title.
result = validate_tool_arguments(
    "create_task",
    {}
)

report_test(
    "Missing create_task title",
    result.get(
        "valid"
    ) is False,
    result
)


# note: Blank task titles fail closed.
result = validate_tool_arguments(
    "create_task",
    {
        "title": "   "
    }
)

report_test(
    "Reject blank create_task title",
    result.get(
        "valid"
    ) is False,
    result
)


# note: Task titles must be plain text.
result = validate_tool_arguments(
    "create_task",
    {
        "title": 123
    }
)

report_test(
    "Reject non-string create_task title",
    result.get(
        "valid"
    ) is False,
    result
)


# note: Task titles are bounded to the same 500-character
# limit enforced by the task storage tool.
result = validate_tool_arguments(
    "create_task",
    {
        "title": "a" * 501
    }
)

report_test(
    "Reject oversized create_task title",
    result.get(
        "valid"
    ) is False,
    result
)


# note: Natural-language dates are intentionally unsupported
# at this deterministic layer.
result = validate_tool_arguments(
    "create_task",
    {
        "title": "finish report",
        "due_date": "tomorrow"
    }
)

report_test(
    "Reject natural-language task due date",
    result.get(
        "valid"
    ) is False,
    result
)


# note: Alternate date formats fail closed.
result = validate_tool_arguments(
    "create_task",
    {
        "title": "finish report",
        "due_date": "09-10-2026"
    }
)

report_test(
    "Reject alternate task due-date format",
    result.get(
        "valid"
    ) is False,
    result
)


# note: Unrelated arguments cannot be injected into creation.
result = validate_tool_arguments(
    "create_task",
    {
        "title": "review logs",
        "priority": "high"
    }
)

report_test(
    "Reject unexpected create_task argument",
    result.get(
        "valid"
    ) is False,
    result
)


# note: list_tasks is a true safe-read zero-argument tool.
result = validate_tool_arguments(
    "list_tasks",
    {}
)

report_test(
    "Valid list_tasks arguments",
    result.get(
        "valid"
    ) is True,
    result
)


# note: Arguments cannot be injected into list_tasks.
result = validate_tool_arguments(
    "list_tasks",
    {
        "path": "../"
    }
)

report_test(
    "Reject list_tasks argument injection",
    result.get(
        "valid"
    ) is False,
    result
)


# note: Normal task-search terms are accepted.
result = validate_tool_arguments(
    "search_tasks",
    {
        "query": "audit"
    }
)

report_test(
    "Valid search_tasks query",
    result.get(
        "valid"
    ) is True,
    result
)


# note: Task search requires its query.
result = validate_tool_arguments(
    "search_tasks",
    {}
)

report_test(
    "Missing search_tasks query",
    result.get(
        "valid"
    ) is False,
    result
)


# note: Empty task-search queries fail closed.
result = validate_tool_arguments(
    "search_tasks",
    {
        "query": "   "
    }
)

report_test(
    "Reject blank search_tasks query",
    result.get(
        "valid"
    ) is False,
    result
)


# note: Task-search queries must be text.
result = validate_tool_arguments(
    "search_tasks",
    {
        "query": 123
    }
)

report_test(
    "Reject non-string search_tasks query",
    result.get(
        "valid"
    ) is False,
    result
)


# note: Task-search queries use the same bounded 200-character
# deterministic input policy as the task tool.
result = validate_tool_arguments(
    "search_tasks",
    {
        "query": "a" * 201
    }
)

report_test(
    "Reject oversized search_tasks query",
    result.get(
        "valid"
    ) is False,
    result
)


# note: filter_tasks accepts only open or completed.
result = validate_tool_arguments(
    "filter_tasks",
    {
        "status": "open"
    }
)

report_test(
    "Valid open task status",
    result.get(
        "valid"
    ) is True,
    result
)


result = validate_tool_arguments(
    "filter_tasks",
    {
        "status": "completed"
    }
)

report_test(
    "Valid completed task status",
    result.get(
        "valid"
    ) is True,
    result
)


# note: Status normalization remains deterministic.
result = validate_tool_arguments(
    "filter_tasks",
    {
        "status": " Completed "
    }
)

report_test(
    "Normalize completed task status",
    result.get(
        "valid"
    ) is True,
    result
)


# note: Unsupported task statuses fail closed.
result = validate_tool_arguments(
    "filter_tasks",
    {
        "status": "pending"
    }
)

report_test(
    "Reject unsupported task status",
    result.get(
        "valid"
    ) is False,
    result
)


# note: Task IDs must be exact positive integers for completion.
result = validate_tool_arguments(
    "complete_task",
    {
        "task_id": 3
    }
)

report_test(
    "Valid complete_task ID",
    result.get(
        "valid"
    ) is True,
    result
)


# note: Completion rejects invalid ID forms.
for invalid_id in [
    0,
    -1,
    "3",
    3.5,
    True,
    None
]:

    result = validate_tool_arguments(
        "complete_task",
        {
            "task_id": invalid_id
        }
    )

    report_test(
        f"Reject complete_task ID {invalid_id!r}",
        result.get(
            "valid"
        ) is False,
        result
    )


# note: Task IDs must also be exact positive integers for
# destructive deletion.
result = validate_tool_arguments(
    "delete_task",
    {
        "task_id": 5
    }
)

report_test(
    "Valid delete_task ID",
    result.get(
        "valid"
    ) is True,
    result
)


# note: Deletion rejects zero, negative, strings, floats,
# booleans, and missing values.
for invalid_id in [
    0,
    -1,
    "5",
    5.5,
    True,
    None
]:

    result = validate_tool_arguments(
        "delete_task",
        {
            "task_id": invalid_id
        }
    )

    report_test(
        f"Reject delete_task ID {invalid_id!r}",
        result.get(
            "valid"
        ) is False,
        result
    )


# note: Verify the argument layer rejects unknown tools.
result = validate_tool_arguments(
    "unknown_tool",
    {}
)

report_test(
    "Unknown tool",
    result.get(
        "valid"
    ) is False,
    result
)


print(
    "\nTool Argument Preparation Tests\n"
)


# note: Verify extraction and validation work together for
# controlled note creation.
result = prepare_tool_arguments(
    "create_note",
    "Create a note that says router test."
)

report_test(
    "Prepare note arguments",
    (
        result.get(
            "success"
        ) is True
        and result.get(
            "arguments"
        ) == {
            "content": "router test."
        }
    ),
    result
)


# note: Verify conversational note creation remains supported.
result = prepare_tool_arguments(
    "create_note",
    (
        "Please save a note for me reminding me "
        "to review the audit logs."
    )
)


# note: Verify conversational note creation remains supported.
result = prepare_tool_arguments(
    "create_note",
    (
        "Please save a note for me reminding me "
        "to review the audit logs."
    )
)

report_test(
    "Prepare conversational note",
    (
        result.get(
            "success"
        ) is True
        and result.get(
            "arguments"
        ) == {
            "content": "review the audit logs."
        }
    ),
    result
)


# note: Verify Step 29F natural write-down phrasing prepares
# valid create_note arguments without model-generated content.
result = prepare_tool_arguments(
    "create_note",
    "Write down that Step 29F live testing has started."
)

report_test(
    "Prepare Step 29F write-down note",
    (
        result.get(
            "success"
        ) is True
        and result.get(
            "arguments"
        ) == {
            "content": "Step 29F live testing has started."
        }
    ),
    result
)

# note: Verify a bare create command fails closed because
# no content can be determined.
result = prepare_tool_arguments(
    "create_note",
    "Create a note."
)

report_test(
    "Missing note content",
    result.get(
        "success"
    ) is False,
    result
)


# note: Verify a no-argument time request remains supported.
result = prepare_tool_arguments(
    "get_current_datetime",
    "What time is it?"
)

report_test(
    "Prepare time arguments",
    (
        result.get(
            "success"
        ) is True
        and result.get(
            "arguments"
        ) == {}
    ),
    result
)


# note: Verify Step 27A note listing prepares no arguments.
result = prepare_tool_arguments(
    "list_notes",
    "Show me my notes."
)

report_test(
    "Prepare list_notes arguments",
    (
        result.get(
            "success"
        ) is True
        and result.get(
            "arguments"
        ) == {}
    ),
    result
)


# note: Verify the exact Step 27B regression case correctly
# preserves the generated JARVIS note filename.
result = prepare_tool_arguments(
    "read_note",
    f"Read {NOTE_FILENAME}"
)

report_test(
    "Prepare read_note arguments",
    (
        result.get(
            "success"
        ) is True
        and result.get(
            "arguments"
        ) == {
            "filename": NOTE_FILENAME
        }
    ),
    result
)


# note: Verify vague note-reading language fails argument
# preparation instead of selecting or inventing a filename.
result = prepare_tool_arguments(
    "read_note",
    "Open note."
)

report_test(
    "Reject ambiguous read_note arguments",
    result.get(
        "success"
    ) is False,
    result
)


# note: Verify an explicit path fails argument validation even
# if it reaches read_note preparation directly.
result = prepare_tool_arguments(
    "read_note",
    "Read ../../Desktop/test.txt"
)

report_test(
    "Reject prepared filesystem path",
    result.get(
        "success"
    ) is False,
    result
)


# note: Verify Step 27C extraction and validation work
# together for a standard note search.
result = prepare_tool_arguments(
    "search_notes",
    "Search my notes for audit"
)

report_test(
    "Prepare search_notes arguments",
    (
        result.get(
            "success"
        ) is True
        and result.get(
            "arguments"
        ) == {
            "query": "audit"
        }
    ),
    result
)


# note: Verify the alternate natural-language search form
# preserves capitalization inside the user's search term.
result = prepare_tool_arguments(
    "search_notes",
    "Which notes mention Phase 5?"
)

report_test(
    "Prepare mention search arguments",
    (
        result.get(
            "success"
        ) is True
        and result.get(
            "arguments"
        ) == {
            "query": "Phase 5"
        }
    ),
    result
)


# note: Verify quoted multi-word search terms are cleaned
# before being sent to the note-search tool.
result = prepare_tool_arguments(
    "search_notes",
    'Search my notes for "audit logs"'
)

report_test(
    "Prepare quoted search arguments",
    (
        result.get(
            "success"
        ) is True
        and result.get(
            "arguments"
        ) == {
            "query": "audit logs"
        }
    ),
    result
)


# note: Verify an incomplete search request fails argument
# preparation instead of manufacturing a query.
result = prepare_tool_arguments(
    "search_notes",
    "Search my notes for "
)

report_test(
    "Reject incomplete search arguments",
    result.get(
        "success"
    ) is False,
    result
)


# note: Verify Step 27D extraction and validation work
# together for a valid exact note edit.
result = prepare_tool_arguments(
    "edit_note",
    (
        f"Edit {NOTE_EDIT_FILENAME} "
        "to say review the new audit logs."
    )
)

report_test(
    "Prepare edit_note arguments",
    (
        result.get(
            "success"
        ) is True
        and result.get(
            "arguments"
        ) == {
            "filename": NOTE_EDIT_FILENAME,
            "content": "review the new audit logs."
        }
    ),
    result
)


# note: Verify quoted filenames and replacement content are
# cleaned correctly during edit preparation.
result = prepare_tool_arguments(
    "edit_note",
    (
        f'Edit "{NOTE_EDIT_FILENAME}" '
        'to say "quoted replacement content."'
    )
)

report_test(
    "Prepare quoted edit_note arguments",
    (
        result.get(
            "success"
        ) is True
        and result.get(
            "arguments"
        ) == {
            "filename": NOTE_EDIT_FILENAME,
            "content": "quoted replacement content."
        }
    ),
    result
)


# note: Verify edit preparation rejects traversal even when
# the command otherwise contains valid replacement content.
result = prepare_tool_arguments(
    "edit_note",
    "Edit ../../Desktop/test.txt to say hacked."
)

report_test(
    "Reject prepared edit path traversal",
    result.get(
        "success"
    ) is False,
    result
)


# note: Verify ordinary files cannot be converted into edit
# targets during argument preparation.
result = prepare_tool_arguments(
    "edit_note",
    "Edit ordinary_file.txt to say changed."
)

report_test(
    "Reject prepared non-JARVIS edit filename",
    result.get(
        "success"
    ) is False,
    result
)


# note: Verify an edit request without replacement content
# fails closed before reaching the permission pipeline.
result = prepare_tool_arguments(
    "edit_note",
    f"Edit {NOTE_EDIT_FILENAME}"
)

report_test(
    "Reject incomplete edit_note arguments",
    result.get(
        "success"
    ) is False,
    result
)


# note: Verify Step 27E extraction and validation work together
# for an exact JARVIS-generated note deletion request.
result = prepare_tool_arguments(
    "delete_note",
    f"Delete {NOTE_DELETE_FILENAME}"
)

report_test(
    "Prepare delete_note arguments",
    (
        result.get(
            "success"
        ) is True
        and result.get(
            "arguments"
        ) == {
            "filename": NOTE_DELETE_FILENAME
        }
    ),
    result
)


# note: Verify quoted exact filenames remain valid deletion
# targets after argument preparation.
result = prepare_tool_arguments(
    "delete_note",
    f'Delete "{NOTE_DELETE_FILENAME}"'
)

report_test(
    "Prepare quoted delete_note arguments",
    (
        result.get(
            "success"
        ) is True
        and result.get(
            "arguments"
        ) == {
            "filename": NOTE_DELETE_FILENAME
        }
    ),
    result
)


# note: Verify vague note deletion cannot manufacture an
# executable target.
result = prepare_tool_arguments(
    "delete_note",
    "Delete my note."
)

report_test(
    "Reject ambiguous delete_note arguments",
    result.get(
        "success"
    ) is False,
    result
)


# note: Verify bulk note deletion language fails closed.
result = prepare_tool_arguments(
    "delete_note",
    "Delete all my notes."
)

report_test(
    "Reject bulk delete_note arguments",
    result.get(
        "success"
    ) is False,
    result
)


# note: Verify descriptive deletion targets fail validation
# because JARVIS requires the exact generated filename.
result = prepare_tool_arguments(
    "delete_note",
    "Delete the audit note."
)

report_test(
    "Reject descriptive delete_note target",
    result.get(
        "success"
    ) is False,
    result
)


# note: Verify traversal targets fail before the destructive
# permission pipeline can be reached.
result = prepare_tool_arguments(
    "delete_note",
    "Delete ../../Desktop/test.txt"
)

report_test(
    "Reject prepared delete path traversal",
    result.get(
        "success"
    ) is False,
    result
)


# note: Verify absolute filesystem targets cannot become
# prepared JARVIS deletion arguments.
result = prepare_tool_arguments(
    "delete_note",
    "Delete /etc/passwd"
)

report_test(
    "Reject prepared absolute delete path",
    result.get(
        "success"
    ) is False,
    result
)


# note: Verify an ordinary text file cannot be converted into
# a controlled JARVIS deletion target.
result = prepare_tool_arguments(
    "delete_note",
    "Delete ordinary_file.txt"
)

report_test(
    "Reject prepared non-JARVIS delete filename",
    result.get(
        "success"
    ) is False,
    result
)


# note: Verify wrong file extensions fail closed during
# destructive argument preparation.
result = prepare_tool_arguments(
    "delete_note",
    "Delete note_test.json"
)

report_test(
    "Reject prepared non-text delete filename",
    result.get(
        "success"
    ) is False,
    result
)


# note: Step 28G verifies task creation preparation without
# an optional due date.
result = prepare_tool_arguments(
    "create_task",
    "Create a task to review the audit logs."
)

report_test(
    "Prepare create_task arguments",
    (
        result.get(
            "success"
        ) is True
        and result.get(
            "arguments"
        ) == {
            "title": "review the audit logs"
        }
    ),
    result
)


# note: Verify strict due-date extraction and validation work
# together before task execution.
result = prepare_tool_arguments(
    "create_task",
    "Create a task to finish the report due 2026-09-10."
)

report_test(
    "Prepare create_task due date",
    (
        result.get(
            "success"
        ) is True
        and result.get(
            "arguments"
        ) == {
            "title": "finish the report",
            "due_date": "2026-09-10"
        }
    ),
    result
)


# note: Bare task creation fails closed.
result = prepare_tool_arguments(
    "create_task",
    "Create a task."
)

report_test(
    "Reject incomplete create_task arguments",
    result.get(
        "success"
    ) is False,
    result
)


# note: Natural-language scheduling remains deliberately
# outside the current task tool contract.
result = prepare_tool_arguments(
    "create_task",
    "Create a task to finish the report due tomorrow."
)

report_test(
    "Reject natural-language prepared due date",
    result.get(
        "success"
    ) is False,
    result
)


# note: Task listing prepares an empty argument dictionary.
result = prepare_tool_arguments(
    "list_tasks",
    "Show my tasks."
)

report_test(
    "Prepare list_tasks arguments",
    (
        result.get(
            "success"
        ) is True
        and result.get(
            "arguments"
        ) == {}
    ),
    result
)


# note: Task search preparation preserves a clean query.
result = prepare_tool_arguments(
    "search_tasks",
    "Search my tasks for audit."
)

report_test(
    "Prepare search_tasks arguments",
    (
        result.get(
            "success"
        ) is True
        and result.get(
            "arguments"
        ) == {
            "query": "audit"
        }
    ),
    result
)


# note: Alternate supported task-search language remains
# deterministic.
result = prepare_tool_arguments(
    "search_tasks",
    "Find tasks containing router."
)


# note: Alternate supported task-search language remains
# deterministic.
result = prepare_tool_arguments(
    "search_tasks",
    "Find tasks containing router."
)

report_test(
    "Prepare alternate search_tasks arguments",
    (
        result.get(
            "success"
        ) is True
        and result.get(
            "arguments"
        ) == {
            "query": "router"
        }
    ),
    result
)


# note: Verify Step 29F singular-task wording prepares the
# exact deterministic search query used during live testing.
result = prepare_tool_arguments(
    "search_tasks",
    "Can you find the task where I mentioned audit logs?"
)

report_test(
    "Prepare Step 29F natural task search",
    (
        result.get(
            "success"
        ) is True
        and result.get(
            "arguments"
        ) == {
            "query": "audit logs"
        }
    ),
    result
)

# note: Incomplete task-search requests fail closed.
result = prepare_tool_arguments(
    "search_tasks",
    "Search my tasks."
)

report_test(
    "Reject incomplete search_tasks arguments",
    result.get(
        "success"
    ) is False,
    result
)


# note: Open-task filtering prepares the exact supported state.
result = prepare_tool_arguments(
    "filter_tasks",
    "Show my open tasks."
)

report_test(
    "Prepare open filter_tasks arguments",
    (
        result.get(
            "success"
        ) is True
        and result.get(
            "arguments"
        ) == {
            "status": "open"
        }
    ),
    result
)


# note: Completed-task filtering prepares the exact supported
# completed state.
result = prepare_tool_arguments(
    "filter_tasks",
    "Show my completed tasks."
)

report_test(
    "Prepare completed filter_tasks arguments",
    (
        result.get(
            "success"
        ) is True
        and result.get(
            "arguments"
        ) == {
            "status": "completed"
        }
    ),
    result
)


# note: Unsupported status wording cannot become executable
# filter arguments.
result = prepare_tool_arguments(
    "filter_tasks",
    "Show my pending tasks."
)

report_test(
    "Reject unsupported filter_tasks arguments",
    result.get(
        "success"
    ) is False,
    result
)


# note: Task completion preparation requires an exact numeric
# ID and converts it to an integer.
result = prepare_tool_arguments(
    "complete_task",
    "Complete task 3."
)

report_test(
    "Prepare complete_task arguments",
    (
        result.get(
            "success"
        ) is True
        and result.get(
            "arguments"
        ) == {
            "task_id": 3
        }
    ),
    result
)


# note: Alternate completion wording remains supported.
result = prepare_tool_arguments(
    "complete_task",
    "Mark task 4 complete."
)

report_test(
    "Prepare alternate complete_task arguments",
    (
        result.get(
            "success"
        ) is True
        and result.get(
            "arguments"
        ) == {
            "task_id": 4
        }
    ),
    result
)


# note: Descriptive completion requests cannot guess an ID.
result = prepare_tool_arguments(
    "complete_task",
    "Complete the audit task."
)

report_test(
    "Reject descriptive complete_task target",
    result.get(
        "success"
    ) is False,
    result
)


# note: Task deletion preparation requires an exact numeric ID.
result = prepare_tool_arguments(
    "delete_task",
    "Delete task 5."
)

report_test(
    "Prepare delete_task arguments",
    (
        result.get(
            "success"
        ) is True
        and result.get(
            "arguments"
        ) == {
            "task_id": 5
        }
    ),
    result
)


# note: Alternate delete wording remains deterministic.
result = prepare_tool_arguments(
    "delete_task",
    "Remove task 6."
)

report_test(
    "Prepare alternate delete_task arguments",
    (
        result.get(
            "success"
        ) is True
        and result.get(
            "arguments"
        ) == {
            "task_id": 6
        }
    ),
    result
)


# note: Descriptive deletion requests cannot guess an ID.
result = prepare_tool_arguments(
    "delete_task",
    "Delete the audit task."
)

report_test(
    "Reject descriptive delete_task target",
    result.get(
        "success"
    ) is False,
    result
)


# note: Zero is not a valid persistent task identifier.
result = prepare_tool_arguments(
    "delete_task",
    "Delete task 0."
)

report_test(
    "Reject zero delete_task ID",
    result.get(
        "success"
    ) is False,
    result
)


# note: Print the final argument-regression summary.
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


# note: Return a nonzero exit status whenever an argument
# regression is detected.
if failed:

    raise SystemExit(
        1
    )
