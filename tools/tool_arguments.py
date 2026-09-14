# note: Define the argument fields currently supported by
# JARVIS's registered tools.
TOOL_ARGUMENT_SCHEMAS = {

    "get_system_info": {
        "required": [],
        "optional": []
    },

    "get_current_datetime": {
        "required": [],
        "optional": []
    },

    "list_project_directory": {
        "required": [],
        "optional": []
    },

    "create_note": {
        "required": [
            "content"
        ],
        "optional": []
    },

    "list_notes": {
        "required": [],
        "optional": []
    },

    "read_note": {
        "required": [
            "filename"
        ],
        "optional": []
    },

    "search_notes": {
        "required": [
            "query"
        ],
        "optional": []
    },

    "edit_note": {
        "required": [
            "filename",
            "content"
        ],
        "optional": []
    },

    # note: Step 27E deletion requires exactly one explicit
    # JARVIS note filename and no additional arguments.
    "delete_note": {
        "required": [
            "filename"
        ],
        "optional": []
    },

    # note: Step 28G task creation requires an explicit title
    # while allowing one optional strict YYYY-MM-DD due date.
    "create_task": {
        "required": [
            "title"
        ],
        "optional": [
            "due_date"
        ]
    },

    # note: Task listing requires no user-supplied arguments.
    "list_tasks": {
        "required": [],
        "optional": []
    },

    # note: Task searching requires one explicit title-search query.
    "search_tasks": {
        "required": [
            "query"
        ],
        "optional": []
    },

    # note: Task filtering accepts exactly one approved status.
    "filter_tasks": {
        "required": [
            "status"
        ],
        "optional": []
    },

    # note: Task completion requires one exact numeric task ID.
    "complete_task": {
        "required": [
            "task_id"
        ],
        "optional": []
    },

    # note: Task deletion requires one exact numeric task ID.
    "delete_task": {
        "required": [
            "task_id"
        ],
        "optional": []
    },

    "test_confirmed_action": {
        "required": [],
        "optional": []
    },

    "test_blocked_action": {
        "required": [],
        "optional": []
    }
}


# note: Normalize extracted text without changing the meaning
# of the user's requested tool argument.
def clean_argument_text(
    text
):

    """Clean extracted argument text."""

    if not isinstance(
        text,
        str
    ):

        return None


    cleaned = text.strip()


    if not cleaned:

        return None


    return cleaned


# note: Extract note content from common natural-language
# note creation requests without requiring one exact phrase.
def extract_note_content(
    request
):

    """Extract note content from a user request."""

    if not isinstance(
        request,
        str
    ):

        return None


    text = request.strip()

    lowered = text.lower()


    prefixes = [
        "please create a note that says ",
        "please make a note that says ",
        "please write a note that says ",
        "please save a note that says ",
        "please create a note saying ",
        "please make a note saying ",
        "please write a note saying ",
        "please save a note saying ",
        "create a note that says ",
        "make a note that says ",
        "write a note that says ",
        "save a note that says ",
        "create a note saying ",
        "make a note saying ",
        "write a note saying ",
        "save a note saying ",
        "create a note to ",
        "make a note to ",
        "write a note to ",
        "save a note to ",
        "create a note: ",
        "make a note: ",
        "write a note: ",
        "save a note: "
    ]


    for prefix in prefixes:

        if lowered.startswith(
            prefix
        ):

            extracted = text[
                len(prefix):
            ]

            return clean_argument_text(
                extracted
            )


    conversational_prefixes = [
        "please save a note for me ",
        "please create a note for me ",
        "please make a note for me ",
        "please write a note for me ",
        "save a note for me ",
        "create a note for me ",
        "make a note for me ",
        "write a note for me "
    ]


    for prefix in conversational_prefixes:

        if lowered.startswith(
            prefix
        ):

            extracted = text[
                len(prefix):
            ]


            connective_prefixes = [
                "reminding me to ",
                "remind me to ",
                "saying ",
                "that says ",
                "to "
            ]


            extracted_lowered = extracted.lower()


            for connective in connective_prefixes:

                if extracted_lowered.startswith(
                    connective
                ):

                    extracted = extracted[
                        len(connective):
                    ]

                    break


            return clean_argument_text(
                extracted
            )


    # note: Support a bounded natural note-writing form such as
    # "Write down that Step 29F testing has started." without
    # allowing arbitrary conversational text to become note content.
    write_down_prefixes = [
        "please write down that ",
        "please write down ",
        "write down that ",
        "write down "
    ]


    for prefix in write_down_prefixes:

        if lowered.startswith(
            prefix
        ):

            extracted = text[
                len(prefix):
            ]

            return clean_argument_text(
                extracted
            )


    return None

# note: Extract one explicit JARVIS note filename from a
# deterministic read or open request.
def extract_note_filename(
    request
):

    """Extract a JARVIS note filename from a user request."""

    if not isinstance(
        request,
        str
    ):

        return None


    text = request.strip()


    # note: Remove only trailing conversational punctuation.
    text = text.rstrip(
        "?!. "
    )


    lowered = text.lower()


    command_prefixes = [
        "please read ",
        "please open ",
        "please show me ",
        "read ",
        "open ",
        "show me "
    ]


    for prefix in command_prefixes:

        if lowered.startswith(
            prefix
        ):

            filename = text[
                len(prefix):
            ].strip()


            # note: Reject vague descriptions rather than
            # inventing a filename.
            vague_targets = {
                "note",
                "a note",
                "the note",
                "file",
                "a file",
                "the file"
            }


            if filename.lower() in vague_targets:

                return None


            optional_prefixes = [
                "the note ",
                "the file ",
                "file "
            ]


            filename_lowered = filename.lower()


            for optional_prefix in optional_prefixes:

                if filename_lowered.startswith(
                    optional_prefix
                ):

                    filename = filename[
                        len(optional_prefix):
                    ].strip()

                    break


            # note: Remove optional surrounding quotation marks.
            if (
                len(
                    filename
                ) >= 2
                and filename[
                    0
                ] in {
                    '"',
                    "'"
                }
                and filename[
                    -1
                ] == filename[
                    0
                ]
            ):

                filename = filename[
                    1:-1
                ].strip()


            if filename.lower() in vague_targets:

                return None


            return clean_argument_text(
                filename
            )


    return None


# note: Extract a plain-text search query from common
# deterministic and model-routed note-search requests.
def extract_note_search_query(
    request
):

    """Extract a search query from a note-search request."""

    if not isinstance(
        request,
        str
    ):

        return None


    text = request.strip()


    # note: Remove conversational punctuation only from the
    # end so meaningful punctuation inside the query remains.
    text = text.rstrip(
        "?!. "
    ).strip()


    lowered = text.lower()


    search_prefixes = [
        "please search my notes for ",
        "please search notes for ",
        "please find notes containing ",
        "please find my notes containing ",
        "please find notes with ",
        "please find my notes with ",
        "search my notes for ",
        "search notes for ",
        "find notes containing ",
        "find my notes containing ",
        "find notes with ",
        "find my notes with ",
        "which notes mention ",
        "what notes mention ",
        "which notes contain ",
        "what notes contain ",

        # note: Support natural read-only phrasing that may
        # reach this extractor through model-assisted routing.
        "what have i written down about ",
        "what did i write down about ",
        "what have i saved about ",
        "do i have any notes about ",
        "do i have anything in my notes about ",
        "can you check my notes for ",
        "could you check my notes for "
    ]


    for prefix in search_prefixes:

        if lowered.startswith(
            prefix
        ):

            query = text[
                len(prefix):
            ].strip()


            # note: Allow quoted search terms while preserving
            # the user's actual text.
            if (
                len(
                    query
                ) >= 2
                and query[
                    0
                ] in {
                    '"',
                    "'"
                }
                and query[
                    -1
                ] == query[
                    0
                ]
            ):

                query = query[
                    1:-1
                ].strip()


            return clean_argument_text(
                query
            )


    return None


# note: Extract one exact JARVIS note filename and complete
# replacement content from deterministic edit requests.
def extract_note_edit_arguments(
    request
):

    """Extract a note filename and replacement content."""

    if not isinstance(
        request,
        str
    ):

        return None


    text = request.strip()


    if not text:

        return None


    lowered = text.lower()


    # note: Support only explicit edit commands so JARVIS
    # does not infer destructive write intent from vague wording.
    command_prefixes = [
        "please edit ",
        "please update ",
        "please change ",
        "edit ",
        "update ",
        "change "
    ]


    command_removed = None


    for prefix in command_prefixes:

        if lowered.startswith(
            prefix
        ):

            command_removed = text[
                len(prefix):
            ].strip()

            break


    if not command_removed:

        return None


    # note: Separate the exact filename from replacement text
    # using an explicit deterministic edit connector.
    content_connectors = [
        " to say ",
        " to read ",
        " to contain ",
        " with the content ",
        " with content "
    ]


    command_removed_lowered = (
        command_removed.lower()
    )


    filename = None
    content = None


    for connector in content_connectors:

        connector_index = (
            command_removed_lowered.find(
                connector
            )
        )


        if connector_index == -1:

            continue


        filename = command_removed[
            :connector_index
        ].strip()

        content = command_removed[
            connector_index
            + len(connector):
        ].strip()

        break


    if not filename or not content:

        return None


    # note: Allow natural wording such as "edit the note
    # note_....txt to say ..." without treating "the note"
    # as part of the filename.
    optional_filename_prefixes = [
        "the note ",
        "note ",
        "the file ",
        "file "
    ]


    filename_lowered = filename.lower()


    for prefix in optional_filename_prefixes:

        if filename_lowered.startswith(
            prefix
        ):

            filename = filename[
                len(prefix):
            ].strip()

            break


    # note: Remove optional surrounding quotation marks from
    # the supplied filename while preserving its exact value.
    if (
        len(
            filename
        ) >= 2
        and filename[
            0
        ] in {
            '"',
            "'"
        }
        and filename[
            -1
        ] == filename[
            0
        ]
    ):

        filename = filename[
            1:-1
        ].strip()


    # note: Remove optional surrounding quotation marks from
    # replacement content without rewriting the user's text.
    if (
        len(
            content
        ) >= 2
        and content[
            0
        ] in {
            '"',
            "'"
        }
        and content[
            -1
        ] == content[
            0
        ]
    ):

        content = content[
            1:-1
        ].strip()


    cleaned_filename = clean_argument_text(
        filename
    )

    cleaned_content = clean_argument_text(
        content
    )


    if (
        not cleaned_filename
        or not cleaned_content
    ):

        return None


    return {
        "filename": cleaned_filename,
        "content": cleaned_content
    }


# note: Extract one exact JARVIS note filename from an explicit
# deletion request without guessing vague or descriptive targets.
def extract_note_delete_filename(
    request
):

    """Extract a JARVIS note filename from a delete request."""

    if not isinstance(
        request,
        str
    ):

        return None


    text = request.strip()


    if not text:

        return None


    # note: Remove trailing conversational punctuation while
    # preserving the .txt extension itself.
    text = text.rstrip(
        "?!. "
    )


    lowered = text.lower()


    # note: Only explicit delete/remove commands qualify as
    # deterministic deletion intent.
    command_prefixes = [
        "please delete ",
        "please remove ",
        "delete ",
        "remove "
    ]


    filename = None


    for prefix in command_prefixes:

        if lowered.startswith(
            prefix
        ):

            filename = text[
                len(prefix):
            ].strip()

            break


    if not filename:

        return None


    # note: Reject vague, descriptive, or bulk deletion targets
    # instead of allowing JARVIS to infer which note to destroy.
    vague_targets = {
        "note",
        "a note",
        "the note",
        "my note",
        "notes",
        "my notes",
        "all notes",
        "all my notes",
        "the notes",
        "file",
        "a file",
        "the file"
    }


    if filename.lower() in vague_targets:

        return None


    # note: Allow harmless natural prefixes only when an exact
    # filename still follows them.
    optional_filename_prefixes = [
        "the note ",
        "note ",
        "the file ",
        "file "
    ]


    filename_lowered = filename.lower()


    for prefix in optional_filename_prefixes:

        if filename_lowered.startswith(
            prefix
        ):

            filename = filename[
                len(prefix):
            ].strip()

            break


    # note: Support quoted exact filenames without allowing
    # quoted descriptions to bypass later validation.
    if (
        len(
            filename
        ) >= 2
        and filename[
            0
        ] in {
            '"',
            "'"
        }
        and filename[
            -1
        ] == filename[
            0
        ]
    ):

        filename = filename[
            1:-1
        ].strip()


    if not filename:

        return None


    if filename.lower() in vague_targets:

        return None


    return clean_argument_text(
        filename
    )


# note: Extract a deterministic task title and optional strict
# YYYY-MM-DD due date from explicit task-creation requests.
def extract_task_create_arguments(
    request
):

    """Extract task creation arguments."""

    if not isinstance(
        request,
        str
    ):

        return None


    text = request.strip()


    if not text:

        return None


    # note: Remove normal trailing conversational punctuation
    # without changing punctuation inside the task text.
    text = text.rstrip(
        "?!. "
    ).strip()


    lowered = text.lower()


    command_prefixes = [
        "please create a task to ",
        "please add a task to ",
        "please create a task ",
        "please add a task ",
        "create a task to ",
        "add a task to ",
        "create a task ",
        "add a task "
    ]


    task_text = None


    for prefix in command_prefixes:

        if lowered.startswith(
            prefix
        ):

            task_text = text[
                len(prefix):
            ].strip()

            break


    if not task_text:

        return None


    # note: Reject creation requests with no actual task title.
    vague_targets = {
        "task",
        "a task",
        "the task",
        "something"
    }


    if task_text.lower() in vague_targets:

        return None


    task_title = task_text
    due_date = None


    # note: Recognize only an explicit trailing "due YYYY-MM-DD"
    # clause. Natural-language dates are intentionally not guessed.
    due_marker = " due "

    task_text_lowered = task_text.lower()

    due_index = task_text_lowered.rfind(
        due_marker
    )


    if due_index != -1:

        possible_title = task_text[
            :due_index
        ].strip()

        possible_due_date = task_text[
            due_index
            + len(due_marker):
        ].strip()


        if (
            possible_title
            and possible_due_date
        ):

            task_title = possible_title
            due_date = possible_due_date


    cleaned_title = clean_argument_text(
        task_title
    )


    if not cleaned_title:

        return None


    arguments = {
        "title": cleaned_title
    }


    if due_date is not None:

        arguments[
            "due_date"
        ] = due_date


    return arguments


# note: Extract one deterministic task-search query from
# explicit or model-routed read-only search requests.
def extract_task_search_query(
    request
):

    """Extract a task-search query."""

    if not isinstance(
        request,
        str
    ):

        return None


    text = request.strip()


    if not text:

        return None


    # note: Remove normal trailing conversational punctuation
    # without changing punctuation inside the task text.
    text = text.rstrip(
        "?!. "
    ).strip()


    lowered = text.lower()


    search_prefixes = [
        "please search my tasks for ",
        "please search tasks for ",
        "please find tasks containing ",
        "please find my tasks containing ",
        "please find tasks with ",
        "please find my tasks with ",
        "search my tasks for ",
        "search tasks for ",
        "find tasks containing ",
        "find my tasks containing ",
        "find tasks with ",
        "find my tasks with ",
        "which tasks mention ",
        "what tasks mention ",
        "which tasks contain ",
        "what tasks contain ",
        "do i have any tasks about ",
        "do i have a task about ",
        "can you check my tasks for ",
        "could you check my tasks for "
    ]


    for prefix in search_prefixes:

        if lowered.startswith(
            prefix
        ):

            query = text[
                len(prefix):
            ].strip()


            if (
                len(
                    query
                ) >= 2
                and query[
                    0
                ] in {
                    '"',
                    "'"
                }
                and query[
                    -1
                ] == query[
                    0
                ]
            ):

                query = query[
                    1:-1
                ].strip()


            return clean_argument_text(
                query
            )


    # note: Support bounded read-only phrasing such as
    # "find the task where I mentioned audit logs" while
    # extracting only the user's explicit search term.
    mentioned_task_prefixes = [
        "please find the task where i mentioned ",
        "please find a task where i mentioned ",
        "can you find the task where i mentioned ",
        "could you find the task where i mentioned ",
        "find the task where i mentioned ",
        "find a task where i mentioned "
    ]


    for prefix in mentioned_task_prefixes:

        if lowered.startswith(
            prefix
        ):

            query = text[
                len(prefix):
            ].strip()


            return clean_argument_text(
                query
            )


    # note: Support the bounded natural pattern
    # "anything about <query> in my tasks" without allowing
    # the extractor to guess a task from arbitrary wording.
    task_about_prefixes = [
        "can you check whether i have anything about ",
        "could you check whether i have anything about ",
        "can you see whether i have anything about ",
        "do i have anything about ",
        "is there anything about "
    ]


    task_suffixes = [
        " in my tasks",
        " in the tasks",
        " in my task list"
    ]


    for prefix in task_about_prefixes:

        if not lowered.startswith(
            prefix
        ):

            continue


        remainder = text[
            len(prefix):
        ].strip()

        remainder_lowered = remainder.lower()


        for suffix in task_suffixes:

            if not remainder_lowered.endswith(
                suffix
            ):

                continue


            query = remainder[
                :-len(suffix)
            ].strip()


            return clean_argument_text(
                query
            )


    return None


# note: Extract one approved task status from explicit
# open-task or completed-task filtering requests.
def extract_task_filter_status(
    request
):

    """Extract a task status filter."""

    if not isinstance(
        request,
        str
    ):

        return None


    text = request.strip().lower()

    text = text.rstrip(
        "?!. "
    )


    open_requests = {
        "show my open tasks",
        "show me my open tasks",
        "show open tasks",
        "list my open tasks",
        "list open tasks",
        "what are my open tasks",
        "which tasks are open"
    }


    completed_requests = {
        "show my completed tasks",
        "show me my completed tasks",
        "show completed tasks",
        "list my completed tasks",
        "list completed tasks",
        "what are my completed tasks",
        "which tasks are completed"
    }


    if text in open_requests:

        return "open"


    if text in completed_requests:

        return "completed"


    return None


# note: Extract one exact positive integer task ID from explicit
# completion commands without guessing from task titles.
def extract_complete_task_id(
    request
):

    """Extract a task ID from a completion request."""

    if not isinstance(
        request,
        str
    ):

        return None


    text = request.strip()


    if not text:

        return None


    text = text.rstrip(
        "?!. "
    )


    lowered = text.lower()


    command_prefixes = [
        "please mark task ",
        "please complete task ",
        "mark task ",
        "complete task "
    ]


    remainder = None


    for prefix in command_prefixes:

        if lowered.startswith(
            prefix
        ):

            remainder = text[
                len(prefix):
            ].strip()

            break


    if not remainder:

        return None


    lowered_remainder = remainder.lower()


    completion_suffixes = [
        " as completed",
        " completed",
        " as complete",
        " complete"
    ]


    for suffix in completion_suffixes:

        if lowered_remainder.endswith(
            suffix
        ):

            remainder = remainder[
                :-len(suffix)
            ].strip()

            break


    if not remainder.isdigit():

        return None


    task_id = int(
        remainder
    )


    if task_id <= 0:

        return None


    return task_id


# note: Extract one exact positive integer task ID from explicit
# deletion commands without guessing from task titles.
def extract_delete_task_id(
    request
):

    """Extract a task ID from a deletion request."""

    if not isinstance(
        request,
        str
    ):

        return None


    text = request.strip()


    if not text:

        return None


    text = text.rstrip(
        "?!. "
    )


    lowered = text.lower()


    command_prefixes = [
        "please delete task ",
        "please remove task ",
        "delete task ",
        "remove task "
    ]


    remainder = None


    for prefix in command_prefixes:

        if lowered.startswith(
            prefix
        ):

            remainder = text[
                len(prefix):
            ].strip()

            break


    if not remainder:

        return None


    if not remainder.isdigit():

        return None


    task_id = int(
        remainder
    )


    if task_id <= 0:

        return None


    return task_id


# note: Extract arguments for a specific tool using only
# deterministic Python logic.
def extract_tool_arguments(
    tool_name,
    request
):

    """Extract arguments for a registered JARVIS tool."""

    if tool_name in {
        "get_system_info",
        "get_current_datetime",
        "list_project_directory",
        "list_notes",
        "list_tasks",
        "test_confirmed_action",
        "test_blocked_action"
    }:

        return {
            "success": True,
            "arguments": {},
            "error": None
        }


    if tool_name == "create_note":

        content = extract_note_content(
            request
        )


        if not content:

            return {
                "success": False,
                "arguments": {},
                "error": (
                    "Could not determine the note content."
                )
            }


        return {
            "success": True,
            "arguments": {
                "content": content
            },
            "error": None
        }


    if tool_name == "read_note":

        filename = extract_note_filename(
            request
        )


        if not filename:

            return {
                "success": False,
                "arguments": {},
                "error": (
                    "Could not determine which note to read."
                )
            }


        return {
            "success": True,
            "arguments": {
                "filename": filename
            },
            "error": None
        }


    # note: Note searching requires one explicit plain-text
    # query extracted from the request.
    if tool_name == "search_notes":

        query = extract_note_search_query(
            request
        )


        if not query:

            return {
                "success": False,
                "arguments": {},
                "error": (
                    "Could not determine what to search for."
                )
            }


        return {
            "success": True,
            "arguments": {
                "query": query
            },
            "error": None
        }


    # note: Note editing requires both one exact filename and
    # complete replacement content before it can proceed.
    if tool_name == "edit_note":

        edit_arguments = extract_note_edit_arguments(
            request
        )


        if not edit_arguments:

            return {
                "success": False,
                "arguments": {},
                "error": (
                    "Could not determine both the note filename "
                    "and replacement content."
                )
            }


        return {
            "success": True,
            "arguments": edit_arguments,
            "error": None
        }


    # note: Step 27E note deletion requires one explicit exact
    # filename before the request can enter the permission system.
    if tool_name == "delete_note":

        filename = extract_note_delete_filename(
            request
        )


        if not filename:

            return {
                "success": False,
                "arguments": {},
                "error": (
                    "Could not determine which exact note "
                    "to delete."
                )
            }


        return {
            "success": True,
            "arguments": {
                "filename": filename
            },
            "error": None
        }


    # note: Task creation requires an explicit title and allows
    # one optional strict due-date argument.
    if tool_name == "create_task":

        task_arguments = extract_task_create_arguments(
            request
        )


        if not task_arguments:

            return {
                "success": False,
                "arguments": {},
                "error": (
                    "Could not determine the task title."
                )
            }


        return {
            "success": True,
            "arguments": task_arguments,
            "error": None
        }


    # note: Task searching requires one explicit deterministic
    # title-search query.
    if tool_name == "search_tasks":

        query = extract_task_search_query(
            request
        )


        if not query:

            return {
                "success": False,
                "arguments": {},
                "error": (
                    "Could not determine what tasks to search for."
                )
            }


        return {
            "success": True,
            "arguments": {
                "query": query
            },
            "error": None
        }


    # note: Task filtering requires one exact supported status
    # derived from deterministic phrasing.
    if tool_name == "filter_tasks":

        status = extract_task_filter_status(
            request
        )


        if not status:

            return {
                "success": False,
                "arguments": {},
                "error": (
                    "Could not determine the task status filter."
                )
            }


        return {
            "success": True,
            "arguments": {
                "status": status
            },
            "error": None
        }


    # note: Task completion requires one exact positive integer
    # ID before entering the confirmation pipeline.
    if tool_name == "complete_task":

        task_id = extract_complete_task_id(
            request
        )


        if task_id is None:

            return {
                "success": False,
                "arguments": {},
                "error": (
                    "Could not determine which exact task "
                    "to complete."
                )
            }


        return {
            "success": True,
            "arguments": {
                "task_id": task_id
            },
            "error": None
        }


    # note: Task deletion requires one exact positive integer
    # ID before entering the confirmation pipeline.
    if tool_name == "delete_task":

        task_id = extract_delete_task_id(
            request
        )


        if task_id is None:

            return {
                "success": False,
                "arguments": {},
                "error": (
                    "Could not determine which exact task "
                    "to delete."
                )
            }


        return {
            "success": True,
            "arguments": {
                "task_id": task_id
            },
            "error": None
        }


    return {
        "success": False,
        "arguments": {},
        "error": (
            f"No argument extractor is configured "
            f"for tool '{tool_name}'."
        )
    }


# note: Validate extracted tool arguments against a
# deterministic schema before execution is considered.
def validate_tool_arguments(
    tool_name,
    arguments
):

    """Validate arguments for a JARVIS tool."""

    if tool_name not in TOOL_ARGUMENT_SCHEMAS:

        return {
            "valid": False,
            "error": (
                f"No argument schema exists for "
                f"tool '{tool_name}'."
            )
        }


    if not isinstance(
        arguments,
        dict
    ):

        return {
            "valid": False,
            "error": (
                "Tool arguments must be a dictionary."
            )
        }


    schema = TOOL_ARGUMENT_SCHEMAS[
        tool_name
    ]


    required_fields = set(
        schema[
            "required"
        ]
    )

    optional_fields = set(
        schema[
            "optional"
        ]
    )

    supplied_fields = set(
        arguments.keys()
    )


    missing_fields = (
        required_fields
        - supplied_fields
    )


    if missing_fields:

        return {
            "valid": False,
            "error": (
                "Missing required tool arguments: "
                + ", ".join(
                    sorted(
                        missing_fields
                    )
                )
            )
        }


    allowed_fields = (
        required_fields
        | optional_fields
    )


    unexpected_fields = (
        supplied_fields
        - allowed_fields
    )


    if unexpected_fields:

        return {
            "valid": False,
            "error": (
                "Unexpected tool arguments: "
                + ", ".join(
                    sorted(
                        unexpected_fields
                    )
                )
            )
        }


    # note: Validate controlled note-writing content.
    if tool_name == "create_note":

        content = arguments.get(
            "content"
        )


        if not isinstance(
            content,
            str
        ):

            return {
                "valid": False,
                "error": (
                    "The note content must be a string."
                )
            }


        if not content.strip():

            return {
                "valid": False,
                "error": (
                    "The note content cannot be empty."
                )
            }


    # note: Validate the note-reading filename before the
    # request reaches the filesystem tool.
    if tool_name == "read_note":

        filename = arguments.get(
            "filename"
        )


        if not isinstance(
            filename,
            str
        ):

            return {
                "valid": False,
                "error": (
                    "The note filename must be a string."
                )
            }


        cleaned_filename = filename.strip()


        if not cleaned_filename:

            return {
                "valid": False,
                "error": (
                    "The note filename cannot be empty."
                )
            }


        if (
            "/" in cleaned_filename
            or "\\" in cleaned_filename
        ):

            return {
                "valid": False,
                "error": (
                    "The note filename cannot contain a path."
                )
            }


        if not cleaned_filename.endswith(
            ".txt"
        ):

            return {
                "valid": False,
                "error": (
                    "The note filename must end in .txt."
                )
            }


        if not cleaned_filename.startswith(
            "note_"
        ):

            return {
                "valid": False,
                "error": (
                    "The filename is not a recognized JARVIS note."
                )
            }


    # note: Validate note-search queries independently from
    # filenames or filesystem paths.
    if tool_name == "search_notes":

        query = arguments.get(
            "query"
        )


        if not isinstance(
            query,
            str
        ):

            return {
                "valid": False,
                "error": (
                    "The note search query must be a string."
                )
            }


        cleaned_query = query.strip()


        if not cleaned_query:

            return {
                "valid": False,
                "error": (
                    "The note search query cannot be empty."
                )
            }


        # note: Keep note searches intentionally bounded at
        # the argument layer as well as the tool layer.
        if len(
            cleaned_query
        ) > 200:

            return {
                "valid": False,
                "error": (
                    "The note search query is too long."
                )
            }


    # note: Validate note-edit arguments before a write request
    # can enter JARVIS's confirmation and execution pipeline.
    if tool_name == "edit_note":

        filename = arguments.get(
            "filename"
        )

        content = arguments.get(
            "content"
        )


        if not isinstance(
            filename,
            str
        ):

            return {
                "valid": False,
                "error": (
                    "The note filename must be a string."
                )
            }


        cleaned_filename = filename.strip()


        if not cleaned_filename:

            return {
                "valid": False,
                "error": (
                    "The note filename cannot be empty."
                )
            }


        # note: Reject path separators before the edit request
        # is ever allowed to reach the filesystem tool.
        if (
            "/" in cleaned_filename
            or "\\" in cleaned_filename
        ):

            return {
                "valid": False,
                "error": (
                    "The note filename cannot contain a path."
                )
            }


        if not cleaned_filename.endswith(
            ".txt"
        ):

            return {
                "valid": False,
                "error": (
                    "The note filename must end in .txt."
                )
            }


        if not cleaned_filename.startswith(
            "note_"
        ):

            return {
                "valid": False,
                "error": (
                    "The filename is not a recognized JARVIS note."
                )
            }


        if not isinstance(
            content,
            str
        ):

            return {
                "valid": False,
                "error": (
                    "The replacement note content must be a string."
                )
            }


        cleaned_content = content.strip()


        if not cleaned_content:

            return {
                "valid": False,
                "error": (
                    "The replacement note content cannot be empty."
                )
            }


        # note: Keep replacement text intentionally bounded
        # before confirmation and filesystem execution.
        if len(
            cleaned_content
        ) > 10000:

            return {
                "valid": False,
                "error": (
                    "The replacement note content is too long."
                )
            }


    # note: Validate Step 27E deletion targets before a
    # destructive request can enter the confirmation pipeline.
    if tool_name == "delete_note":

        filename = arguments.get(
            "filename"
        )


        if not isinstance(
            filename,
            str
        ):

            return {
                "valid": False,
                "error": (
                    "The note filename must be a string."
                )
            }


        cleaned_filename = filename.strip()


        if not cleaned_filename:

            return {
                "valid": False,
                "error": (
                    "The note filename cannot be empty."
                )
            }


        # note: Reject path separators before delete_note can
        # ever receive a filesystem target.
        if (
            "/" in cleaned_filename
            or "\\" in cleaned_filename
        ):

            return {
                "valid": False,
                "error": (
                    "The note filename cannot contain a path."
                )
            }


        if not cleaned_filename.endswith(
            ".txt"
        ):

            return {
                "valid": False,
                "error": (
                    "The note filename must end in .txt."
                )
            }


        if not cleaned_filename.startswith(
            "note_"
        ):

            return {
                "valid": False,
                "error": (
                    "The filename is not a recognized JARVIS note."
                )
            }


    # note: Validate task creation arguments independently from
    # the task tool so malformed requests fail before confirmation.
    if tool_name == "create_task":

        title = arguments.get(
            "title"
        )


        if not isinstance(
            title,
            str
        ):

            return {
                "valid": False,
                "error": (
                    "The task title must be a string."
                )
            }


        cleaned_title = title.strip()


        if not cleaned_title:

            return {
                "valid": False,
                "error": (
                    "The task title cannot be empty."
                )
            }


        if len(
            cleaned_title
        ) > 500:

            return {
                "valid": False,
                "error": (
                    "The task title is too long."
                )
            }


        due_date = arguments.get(
            "due_date"
        )


        if due_date is not None:

            if not isinstance(
                due_date,
                str
            ):

                return {
                    "valid": False,
                    "error": (
                        "The task due date must be a string."
                    )
                }


            cleaned_due_date = due_date.strip()


            # note: Enforce exact YYYY-MM-DD structure here;
            # calendar validity is checked again by task_tools.py.
            if (
                len(
                    cleaned_due_date
                ) != 10
                or cleaned_due_date[
                    4
                ] != "-"
                or cleaned_due_date[
                    7
                ] != "-"
                or not cleaned_due_date[
                    0:4
                ].isdigit()
                or not cleaned_due_date[
                    5:7
                ].isdigit()
                or not cleaned_due_date[
                    8:10
                ].isdigit()
            ):

                return {
                    "valid": False,
                    "error": (
                        "The task due date must use YYYY-MM-DD format."
                    )
                }


    # note: Validate task-search queries before they reach
    # the local task database.
    if tool_name == "search_tasks":

        query = arguments.get(
            "query"
        )


        if not isinstance(
            query,
            str
        ):

            return {
                "valid": False,
                "error": (
                    "The task search query must be a string."
                )
            }


        cleaned_query = query.strip()


        if not cleaned_query:

            return {
                "valid": False,
                "error": (
                    "The task search query cannot be empty."
                )
            }


        if len(
            cleaned_query
        ) > 200:

            return {
                "valid": False,
                "error": (
                    "The task search query is too long."
                )
            }


    # note: Allow only the two task states currently supported
    # by the local task data model.
    if tool_name == "filter_tasks":

        status = arguments.get(
            "status"
        )


        if not isinstance(
            status,
            str
        ):

            return {
                "valid": False,
                "error": (
                    "The task status must be a string."
                )
            }


        cleaned_status = status.strip().lower()


        if cleaned_status not in {
            "open",
            "completed"
        }:

            return {
                "valid": False,
                "error": (
                    "The task status must be open or completed."
                )
            }


    # note: Completion and deletion both require exact positive
    # integer IDs. Booleans are explicitly rejected because
    # Python bool is a subclass of int.
    if tool_name in {
        "complete_task",
        "delete_task"
    }:

        task_id = arguments.get(
            "task_id"
        )


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

            return {
                "valid": False,
                "error": (
                    "The task ID must be a positive integer."
                )
            }


        if task_id <= 0:

            return {
                "valid": False,
                "error": (
                    "The task ID must be a positive integer."
                )
            }


    return {
        "valid": True,
        "error": None
    }


# note: Provide one entry point that performs both extraction
# and validation before returning usable tool arguments.
def prepare_tool_arguments(
    tool_name,
    request
):

    """Extract and validate arguments for a JARVIS tool."""

    extraction_result = extract_tool_arguments(
        tool_name,
        request
    )


    if not extraction_result.get(
        "success"
    ):

        return {
            "success": False,
            "arguments": {},
            "error": extraction_result.get(
                "error"
            )
        }


    arguments = extraction_result.get(
        "arguments",
        {}
    )


    validation_result = validate_tool_arguments(
        tool_name,
        arguments
    )


    if not validation_result.get(
        "valid"
    ):

        return {
            "success": False,
            "arguments": {},
            "error": validation_result.get(
                "error"
            )
        }


    return {
        "success": True,
        "arguments": arguments,
        "error": None
    }
