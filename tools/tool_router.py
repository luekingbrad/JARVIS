# note: Import regular-expression support so routing can match
# complete words instead of unsafe substring fragments.
import re


# note: Define the routing states used by JARVIS to distinguish
# clear tool requests from ambiguous or unrelated requests.
ROUTE_MATCHED = "matched"
ROUTE_AMBIGUOUS = "ambiguous"
ROUTE_NO_MATCH = "no_match"


# note: Normalize user requests so routing rules can recognize
# variations in capitalization, punctuation, and spacing.
def normalize_request(
    question
):

    """Return a normalized version of a user request."""

    normalized = question.lower().strip()

    punctuation = [
        "?",
        "!",
        ".",
        ",",
        ":",
        ";"
    ]


    for character in punctuation:

        normalized = normalized.replace(
            character,
            ""
        )


    normalized = " ".join(
        normalized.split()
    )


    return normalized


# note: Match complete words so terms such as "day" do not
# accidentally match words such as "today".
def contains_word(
    text,
    word
):

    """Return True when a complete word appears in text."""

    pattern = (
        r"\b"
        + re.escape(
            word
        )
        + r"\b"
    )


    return bool(
        re.search(
            pattern,
            text
        )
    )


# note: Determine whether a request is asking JARVIS for
# information about the computer or runtime environment.
def matches_system_info_request(
    lowered
):

    """Return True for system-information requests."""

    exact_phrases = [
        "what system are you running on",
        "what computer are you running on",
        "what operating system are you running",
        "what operating system am i using",
        "what os are you running",
        "what os am i using",
        "what machine are you running on",
        "what computer is this",
        "what system is this",
        "what is my computer name",
        "what is the computer name",
        "what architecture is this computer",
        "what python version are you running",
        "what python version am i using",
        "show system information",
        "show system info",
        "get system information",
        "get system info"
    ]


    if any(
        phrase in lowered
        for phrase in exact_phrases
    ):

        return True


    system_terms = [
        "system",
        "computer",
        "machine",
        "operating system",
        "architecture",
        "python version",
        "computer name"
    ]

    request_terms = [
        "what",
        "show",
        "tell",
        "give",
        "get",
        "using",
        "running"
    ]


    has_system_term = any(
        term in lowered
        for term in system_terms
    )

    has_request_term = any(
        term in lowered
        for term in request_terms
    )


    return (
        has_system_term
        and has_request_term
    )


# note: Determine whether a request is asking specifically for
# the current date, time, day, or timezone.
def matches_datetime_request(
    lowered
):

    """Return True for current date-and-time requests."""

    exact_phrases = [
        "what time is it",
        "what is the time",
        "whats the time",
        "what date is it",
        "what is the date",
        "whats the date",
        "what day is it",
        "what is todays date",
        "what is today's date",
        "whats todays date",
        "what is the current time",
        "what is the current date",
        "tell me the time",
        "tell me the date",
        "current date and time",
        "what time and date is it"
    ]


    if any(
        phrase == lowered
        for phrase in exact_phrases
    ):

        return True


    temporal_nouns = [
        "time",
        "date",
        "day",
        "timezone"
    ]


    has_temporal_noun = any(
        contains_word(
            lowered,
            noun
        )
        for noun in temporal_nouns
    )


    request_context = [
        "what",
        "tell",
        "give",
        "show",
        "current",
        "now",
        "today"
    ]


    has_request_context = any(
        contains_word(
            lowered,
            term
        )
        for term in request_context
    )


    return (
        has_temporal_noun
        and has_request_context
    )


# note: Determine whether a request clearly asks to inspect
# the approved JARVIS project directory.
def matches_project_directory_request(
    lowered
):

    """Return True for clear project-directory requests."""

    exact_phrases = [
        "list the project directory",
        "list the jarvis directory",
        "list the jarvis folder",
        "show the project directory",
        "show the jarvis directory",
        "show the jarvis folder",
        "what files are in the project",
        "what files are in jarvis",
        "what files are in the jarvis folder",
        "what is in the jarvis folder",
        "what is in the project folder",
        "show project files",
        "list project files"
    ]


    if any(
        phrase in lowered
        for phrase in exact_phrases
    ):

        return True


    location_terms = [
        "jarvis",
        "project"
    ]

    filesystem_terms = [
        "files",
        "folders",
        "directory",
        "contents"
    ]

    inspection_terms = [
        "list",
        "show",
        "inside",
        "contains",
        "contain"
    ]


    has_location = any(
        term in lowered
        for term in location_terms
    )

    has_filesystem_context = any(
        term in lowered
        for term in filesystem_terms
    )

    has_inspection_context = any(
        term in lowered
        for term in inspection_terms
    )


    return (
        has_location
        and has_filesystem_context
        and has_inspection_context
    )


# note: Detect broad references to JARVIS or the project that
# could mean several different things.
def matches_ambiguous_project_request(
    lowered
):

    """Return True for ambiguous project-related requests."""

    ambiguous_phrases = [
        "show me the project",
        "show the project",
        "show me jarvis",
        "show jarvis",
        "open the project",
        "open project",
        "open jarvis",
        "let me see the project",
        "let me see jarvis",
        "take me to the project",
        "take me to jarvis"
    ]


    return lowered in ambiguous_phrases


# note: Determine whether the user clearly wants JARVIS to
# create a controlled local note.
def matches_note_creation_request(
    lowered
):

    """Return True for note-creation requests."""

    creation_prefixes = [
        "create ",
        "make ",
        "write ",
        "save ",
        "please create ",
        "please make ",
        "please write ",
        "please save "
    ]


    has_creation_action = any(
        lowered.startswith(
            prefix
        )
        for prefix in creation_prefixes
    )


    has_note_term = any(
        contains_word(
            lowered,
            term
        )
        for term in [
            "note",
            "notes"
        ]
    )


    # note: Support the bounded natural note-writing forms
    # handled by the deterministic argument extractor.
    write_down_prefixes = [
        "write down that ",
        "write down ",
        "please write down that ",
        "please write down "
    ]


    has_write_down_action = any(
        lowered.startswith(
            prefix
        )
        and len(
            lowered
        ) > len(
            prefix
        )
        for prefix in write_down_prefixes
    )


    return (
        (
            has_creation_action
            and has_note_term
        )
        or has_write_down_action
    )


    """Return True for note-creation requests."""

    creation_prefixes = [
        "create ",
        "make ",
        "write ",
        "save ",
        "please create ",
        "please make ",
        "please write ",
        "please save "
    ]


    has_creation_action = any(
        lowered.startswith(
            prefix
        )
        for prefix in creation_prefixes
    )


    has_note_term = any(
        contains_word(
            lowered,
            term
        )
        for term in [
            "note",
            "notes"
        ]
    )


    return (
        has_creation_action
        and has_note_term
    )


# note: Determine whether the user clearly wants JARVIS to
# list notes stored inside the approved notes directory.
def matches_note_listing_request(
    lowered
):

    """Return True for note-listing requests."""

    exact_phrases = [
        "list my notes",
        "list notes",
        "show my notes",
        "show me my notes",
        "show notes",
        "what notes do i have",
        "what notes are saved",
        "what notes are stored",
        "what notes have i saved",
        "what notes have you saved",
        "what notes do you have",
        "show saved notes",
        "list saved notes"
    ]


    if lowered in exact_phrases:

        return True


    listing_terms = [
        "list",
        "show",
        "what"
    ]

    ownership_terms = [
        "my",
        "saved",
        "stored",
        "have"
    ]


    has_listing_term = any(
        contains_word(
            lowered,
            term
        )
        for term in listing_terms
    )

    has_note_term = any(
        contains_word(
            lowered,
            term
        )
        for term in [
            "note",
            "notes"
        ]
    )

    has_ownership_term = any(
        contains_word(
            lowered,
            term
        )
        for term in ownership_terms
    )


    return (
        has_listing_term
        and has_note_term
        and has_ownership_term
    )


# note: Determine whether a request explicitly identifies one
# JARVIS note filename to read.
def matches_note_read_request(
    lowered
):

    """Return True for clear note-reading requests."""

    read_prefixes = [
        "read ",
        "open ",
        "show me ",
        "please read ",
        "please open ",
        "please show me "
    ]


    has_read_action = any(
        lowered.startswith(
            prefix
        )
        for prefix in read_prefixes
    )


    # note: normalize_request removes the period from .txt,
    # so the router checks the normalized filename markers.
    has_note_filename = (
        "note_" in lowered
        and "txt" in lowered
    )


    return (
        has_read_action
        and has_note_filename
    )


# note: Determine whether a request clearly asks JARVIS to
# search the contents of its approved saved notes.
def matches_note_search_request(
    lowered
):

    """Return True for clear note-search requests."""

    search_prefixes = [
        "search my notes for ",
        "search notes for ",
        "please search my notes for ",
        "please search notes for ",
        "find notes containing ",
        "find my notes containing ",
        "please find notes containing ",
        "please find my notes containing ",
        "find notes with ",
        "find my notes with ",
        "please find notes with ",
        "please find my notes with ",
        "which notes mention ",
        "what notes mention ",
        "which notes contain ",
        "what notes contain "
    ]


    return any(
        lowered.startswith(
            prefix
        )
        and len(
            lowered
        ) > len(
            prefix
        )
        for prefix in search_prefixes
    )


# note: Detect vague requests to search notes when no actual
# search term was supplied.
def matches_ambiguous_note_search_request(
    lowered
):

    """Return True for incomplete note-search requests."""

    incomplete_search_phrases = [
        "search my notes",
        "search notes",
        "search my notes for",
        "search notes for",
        "please search my notes",
        "please search notes",
        "please search my notes for",
        "please search notes for",
        "find notes",
        "find my notes",
        "find notes containing",
        "find my notes containing",
        "find notes with",
        "find my notes with",
        "which notes mention",
        "what notes mention",
        "which notes contain",
        "what notes contain"
    ]


    return lowered in incomplete_search_phrases


# note: Determine whether a request explicitly identifies one
# JARVIS note filename and clearly asks to edit that note.
def matches_note_edit_request(
    lowered
):

    """Return True for clear note-editing requests."""

    edit_prefixes = [
        "edit ",
        "update ",
        "change ",
        "please edit ",
        "please update ",
        "please change "
    ]


    has_edit_action = any(
        lowered.startswith(
            prefix
        )
        for prefix in edit_prefixes
    )


    # note: normalize_request removes the period from .txt,
    # so use the same normalized filename markers as note reads.
    has_note_filename = (
        "note_" in lowered
        and "txt" in lowered
    )


    edit_connectors = [
        " to say ",
        " to read ",
        " to contain ",
        " with the content ",
        " with content "
    ]


    has_edit_connector = any(
        connector in lowered
        for connector in edit_connectors
    )


    return (
        has_edit_action
        and has_note_filename
        and has_edit_connector
    )


# note: Detect vague or incomplete note-edit requests so JARVIS
# never guesses which note or replacement content to modify.
def matches_ambiguous_note_edit_request(
    lowered
):

    """Return True for ambiguous note-editing requests."""

    edit_prefixes = [
        "edit ",
        "update ",
        "change ",
        "please edit ",
        "please update ",
        "please change "
    ]


    has_edit_action = any(
        lowered.startswith(
            prefix
        )
        for prefix in edit_prefixes
    )


    if not has_edit_action:

        return False


    has_note_context = (
        contains_word(
            lowered,
            "note"
        )
        or contains_word(
            lowered,
            "notes"
        )
        or "note_" in lowered
    )


    if not has_note_context:

        return False


    if matches_note_edit_request(
        lowered
    ):

        return False


    return True


# note: Step 27E recognizes deletion only when the user supplies
# one exact JARVIS-generated note filename.
def matches_note_delete_request(
    lowered
):

    """Return True for clear note-deletion requests."""

    delete_prefixes = [
        "delete ",
        "remove ",
        "please delete ",
        "please remove "
    ]


    has_delete_action = any(
        lowered.startswith(
            prefix
        )
        for prefix in delete_prefixes
    )


    has_note_filename = (
        "note_" in lowered
        and "txt" in lowered
    )


    return (
        has_delete_action
        and has_note_filename
    )


# note: Detect vague note-deletion requests so destructive
# intent never falls through to the language model for guessing.
def matches_ambiguous_note_delete_request(
    lowered
):

    """Return True for ambiguous note-deletion requests."""

    delete_prefixes = [
        "delete ",
        "remove ",
        "please delete ",
        "please remove "
    ]


    has_delete_action = any(
        lowered.startswith(
            prefix
        )
        for prefix in delete_prefixes
    )


    if not has_delete_action:

        return False


    if matches_note_delete_request(
        lowered
    ):

        return False


    has_note_context = (
        contains_word(
            lowered,
            "note"
        )
        or contains_word(
            lowered,
            "notes"
        )
        or "note_" in lowered
    )


    return has_note_context


# note: Detect destructive filesystem requests that are not
# approved exact JARVIS note deletions.
def matches_unapproved_delete_request(
    lowered
):

    """Return True for unsupported filesystem deletion."""

    delete_prefixes = [
        "delete ",
        "remove ",
        "please delete ",
        "please remove "
    ]


    has_delete_action = any(
        lowered.startswith(
            prefix
        )
        for prefix in delete_prefixes
    )


    if not has_delete_action:

        return False


    if matches_note_delete_request(
        lowered
    ):

        return False


    # note: Task deletion is handled by its own approved
    # deterministic route and is not a filesystem request.
    if contains_word(
        lowered,
        "task"
    ) or contains_word(
        lowered,
        "tasks"
    ):

        return False


    has_path_separator = (
        "/" in lowered
        or "\\" in lowered
    )


    external_location_terms = [
        "desktop",
        "documents",
        "downloads",
        "home folder",
        "root",
        "/etc",
        "/users",
        "/var",
        "/tmp"
    ]


    has_external_location = any(
        term in lowered
        for term in external_location_terms
    )


    has_text_filename_marker = (
        "txt" in lowered
    )


    return (
        has_path_separator
        or has_external_location
        or has_text_filename_marker
    )


# note: Detect vague note-reading requests so JARVIS does not
# invent a note or let the language model fake file access.
def matches_ambiguous_note_request(
    lowered
):

    """Return True for ambiguous note-related requests."""

    ambiguous_phrases = [
        "note this",
        "my note",
        "the note",
        "open note",
        "open a note",
        "read note",
        "read a note",
        "show me a note",
        "please open note",
        "please open a note",
        "please read note",
        "please read a note",
        "notes"
    ]


    return lowered in ambiguous_phrases


# note: Determine whether the user clearly wants JARVIS to
# create one controlled local task.
def matches_task_creation_request(
    lowered
):

    """Return True for clear task-creation requests."""

    prefixes = [
        "create a task to ",
        "add a task to ",
        "create a task ",
        "add a task ",
        "please create a task to ",
        "please add a task to ",
        "please create a task ",
        "please add a task "
    ]


    return any(
        lowered.startswith(
            prefix
        )
        and len(
            lowered
        ) > len(
            prefix
        )
        for prefix in prefixes
    )


# note: Detect incomplete task-creation requests so JARVIS does
# not create a task without an explicit title.
def matches_ambiguous_task_creation_request(
    lowered
):

    """Return True for incomplete task-creation requests."""

    incomplete_phrases = [
        "create a task",
        "add a task",
        "please create a task",
        "please add a task",
        "create task",
        "add task"
    ]


    return lowered in incomplete_phrases


# note: Determine whether the user clearly wants all tasks
# listed without filtering or searching.
def matches_task_listing_request(
    lowered
):

    """Return True for clear task-listing requests."""

    exact_phrases = [
        "list my tasks",
        "list tasks",
        "show my tasks",
        "show me my tasks",
        "show tasks",
        "what tasks do i have",
        "what tasks are saved",
        "what tasks are stored",
        "what tasks do you have"
    ]


    return lowered in exact_phrases


# note: Determine whether a request clearly searches task
# titles using an explicit query.
def matches_task_search_request(
    lowered
):

    """Return True for clear task-search requests."""

    prefixes = [
        "search my tasks for ",
        "search tasks for ",
        "please search my tasks for ",
        "please search tasks for ",
        "find tasks containing ",
        "find my tasks containing ",
        "please find tasks containing ",
        "please find my tasks containing ",
        "find tasks with ",
        "find my tasks with ",
        "please find tasks with ",
        "please find my tasks with ",
        "which tasks mention ",
        "what tasks mention ",
        "which tasks contain ",
        "what tasks contain "
    ]


    return any(
        lowered.startswith(
            prefix
        )
        and len(
            lowered
        ) > len(
            prefix
        )
        for prefix in prefixes
    )


# note: Detect incomplete task-search requests so JARVIS never
# invents a search term.
def matches_ambiguous_task_search_request(
    lowered
):

    """Return True for incomplete task-search requests."""

    phrases = [
        "search my tasks",
        "search tasks",
        "search my tasks for",
        "search tasks for",
        "please search my tasks",
        "please search tasks",
        "please search my tasks for",
        "please search tasks for",
        "find tasks",
        "find my tasks",
        "find tasks containing",
        "find my tasks containing",
        "find tasks with",
        "find my tasks with",
        "which tasks mention",
        "what tasks mention",
        "which tasks contain",
        "what tasks contain"
    ]


    return lowered in phrases


# note: Determine whether the user wants to filter the local
# task list to one supported status.
def matches_task_filter_request(
    lowered
):

    """Return True for supported task-status filters."""

    phrases = [
        "show my open tasks",
        "show me my open tasks",
        "show open tasks",
        "list my open tasks",
        "list open tasks",
        "what are my open tasks",
        "which tasks are open",
        "show my completed tasks",
        "show me my completed tasks",
        "show completed tasks",
        "list my completed tasks",
        "list completed tasks",
        "what are my completed tasks",
        "which tasks are completed"
    ]


    return lowered in phrases


# note: Detect requests for unsupported task states instead of
# allowing the model to invent a task status.
def matches_ambiguous_task_filter_request(
    lowered
):

    """Return True for unsupported task-status filtering."""

    has_task_context = (
        contains_word(
            lowered,
            "task"
        )
        or contains_word(
            lowered,
            "tasks"
        )
    )


    if not has_task_context:

        return False


    filter_actions = [
        "show",
        "list",
        "what",
        "which"
    ]


    has_filter_action = any(
        contains_word(
            lowered,
            action
        )
        for action in filter_actions
    )


    unsupported_statuses = [
        "pending",
        "incomplete",
        "unfinished",
        "done",
        "active",
        "closed"
    ]


    has_unsupported_status = any(
        contains_word(
            lowered,
            status
        )
        for status in unsupported_statuses
    )


    return (
        has_filter_action
        and has_unsupported_status
    )


# note: Determine whether a request clearly identifies one
# exact numeric task ID to mark completed.
def matches_task_completion_request(
    lowered
):

    """Return True for exact task-completion requests."""

    patterns = [
        r"^(please )?complete task [1-9][0-9]*$",
        r"^(please )?mark task [1-9][0-9]* complete$",
        r"^(please )?mark task [1-9][0-9]* completed$",
        r"^(please )?mark task [1-9][0-9]* as complete$",
        r"^(please )?mark task [1-9][0-9]* as completed$"
    ]


    return any(
        re.fullmatch(
            pattern,
            lowered
        )
        is not None
        for pattern in patterns
    )


# note: Detect task-completion intent without an exact numeric
# ID so JARVIS never guesses which task should change state.
def matches_ambiguous_task_completion_request(
    lowered
):

    """Return True for ambiguous task-completion requests."""

    completion_prefixes = [
        "complete ",
        "mark ",
        "please complete ",
        "please mark "
    ]


    has_completion_action = any(
        lowered.startswith(
            prefix
        )
        for prefix in completion_prefixes
    )


    if not has_completion_action:

        return False


    has_task_context = (
        contains_word(
            lowered,
            "task"
        )
        or contains_word(
            lowered,
            "tasks"
        )
    )


    if not has_task_context:

        return False


    if matches_task_completion_request(
        lowered
    ):

        return False


    return True


# note: Determine whether a request clearly identifies one
# exact numeric task ID to permanently delete.
def matches_task_delete_request(
    lowered
):

    """Return True for exact task-deletion requests."""

    patterns = [
        r"^(please )?delete task [1-9][0-9]*$",
        r"^(please )?remove task [1-9][0-9]*$"
    ]


    return any(
        re.fullmatch(
            pattern,
            lowered
        )
        is not None
        for pattern in patterns
    )


# note: Detect task-deletion intent without an exact numeric ID
# so destructive targeting can never be guessed.
def matches_ambiguous_task_delete_request(
    lowered
):

    """Return True for ambiguous task-deletion requests."""

    delete_prefixes = [
        "delete ",
        "remove ",
        "please delete ",
        "please remove "
    ]


    has_delete_action = any(
        lowered.startswith(
            prefix
        )
        for prefix in delete_prefixes
    )


    if not has_delete_action:

        return False


    has_task_context = (
        contains_word(
            lowered,
            "task"
        )
        or contains_word(
            lowered,
            "tasks"
        )
    )


    if not has_task_context:

        return False


    if matches_task_delete_request(
        lowered
    ):

        return False


    return True


# note: Detect broad task references that cannot safely map to
# one specific task tool.
def matches_ambiguous_task_request(
    lowered
):

    """Return True for vague task-related requests."""

    phrases = [
        "task",
        "tasks",
        "my task",
        "the task",
        "show me a task",
        "show a task",
        "open a task",
        "open task"
    ]


    return lowered in phrases


# note: Determine whether a request refers to the harmless
# confirmation-required permission test tool.
def matches_confirmation_test_request(
    lowered
):

    """Return True for the confirmation test tool."""

    confirmation_test_phrases = [
        "perform the test action",
        "run the test action",
        "execute the test action",
        "perform the confirmation test",
        "run the confirmation test",
        "execute the confirmation test",
        "test confirmation required",
        "test the confirmation system"
    ]


    return any(
        phrase in lowered
        for phrase in confirmation_test_phrases
    )


# note: Determine whether a request refers to the harmless
# blocked permission-test tool.
def matches_blocked_test_request(
    lowered
):

    """Return True for the blocked test tool."""

    blocked_test_phrases = [
        "perform the blocked test",
        "run the blocked test",
        "execute the blocked test",
        "perform the blocked action",
        "run the blocked action",
        "execute the blocked action",
        "test the blocked tool"
    ]


    return any(
        phrase in lowered
        for phrase in blocked_test_phrases
    )


# note: Detect requests that attempt to inspect or read
# filesystem locations outside JARVIS's approved areas.
def matches_unapproved_filesystem_request(
    lowered
):

    """Return True for unsupported filesystem access."""

    filesystem_terms = [
        "file",
        "files",
        "folder",
        "folders",
        "directory",
        "contents"
    ]

    inspection_terms = [
        "show",
        "list",
        "what",
        "inspect",
        "look",
        "see",
        "read",
        "open"
    ]


    has_filesystem_term = any(
        contains_word(
            lowered,
            term
        )
        for term in filesystem_terms
    )

    has_inspection_term = any(
        contains_word(
            lowered,
            term
        )
        for term in inspection_terms
    )


    external_location_terms = [
        "desktop",
        "documents",
        "downloads",
        "home folder",
        "root",
        "/etc",
        "/users",
        "/var",
        "/tmp"
    ]


    has_external_location = any(
        term in lowered
        for term in external_location_terms
    )


    has_path_separator = (
        "/" in lowered
        or "\\" in lowered
    )


    approved_location = (
        "jarvis" in lowered
        or "project" in lowered
    )


    descriptive_filesystem_request = (
        has_filesystem_term
        and has_inspection_term
        and not approved_location
    )


    explicit_external_path_request = (
        has_inspection_term
        and (
            has_external_location
            or has_path_separator
        )
        and not approved_location
    )


    return (
        descriptive_filesystem_request
        or explicit_external_path_request
    )


# note: Classify a user request before selecting a tool so
# JARVIS can distinguish clear matches from ambiguity.
def classify_tool_request(
    question
):

    """Classify a request as matched, ambiguous, or no match."""

    lowered = normalize_request(
        question
    )


    if matches_system_info_request(
        lowered
    ):

        return {
            "status": ROUTE_MATCHED,
            "tool": "get_system_info",
            "reason": "clear_system_info_request"
        }


    if matches_datetime_request(
        lowered
    ):

        return {
            "status": ROUTE_MATCHED,
            "tool": "get_current_datetime",
            "reason": "clear_datetime_request"
        }


    if matches_project_directory_request(
        lowered
    ):

        return {
            "status": ROUTE_MATCHED,
            "tool": "list_project_directory",
            "reason": "clear_project_directory_request"
        }


    if matches_ambiguous_project_request(
        lowered
    ):

        return {
            "status": ROUTE_AMBIGUOUS,
            "tool": None,
            "reason": "ambiguous_project_request"
        }


    # note: Keep note creation ahead of generic task routes so
    # existing note behavior remains unchanged.
    if matches_note_creation_request(
        lowered
    ):

        return {
            "status": ROUTE_MATCHED,
            "tool": "create_note",
            "reason": "clear_note_creation_request"
        }


    # note: Exact note deletion retains priority over broader
    # destructive-request detection.
    if matches_note_delete_request(
        lowered
    ):

        return {
            "status": ROUTE_MATCHED,
            "tool": "delete_note",
            "reason": "clear_note_delete_request"
        }


    if matches_ambiguous_note_delete_request(
        lowered
    ):

        return {
            "status": ROUTE_AMBIGUOUS,
            "tool": None,
            "reason": "ambiguous_note_delete_request"
        }


    # note: Task creation is checked before general task
    # listing or ambiguity handling.
    if matches_task_creation_request(
        lowered
    ):

        return {
            "status": ROUTE_MATCHED,
            "tool": "create_task",
            "reason": "clear_task_creation_request"
        }


    if matches_ambiguous_task_creation_request(
        lowered
    ):

        return {
            "status": ROUTE_AMBIGUOUS,
            "tool": None,
            "reason": "ambiguous_task_creation_request"
        }


    # note: Exact task deletion is evaluated before generic
    # deletion denial because task deletion is an approved tool.
    if matches_task_delete_request(
        lowered
    ):

        return {
            "status": ROUTE_MATCHED,
            "tool": "delete_task",
            "reason": "clear_task_delete_request"
        }


    if matches_ambiguous_task_delete_request(
        lowered
    ):

        return {
            "status": ROUTE_AMBIGUOUS,
            "tool": None,
            "reason": "ambiguous_task_delete_request"
        }


    if matches_unapproved_delete_request(
        lowered
    ):

        return {
            "status": ROUTE_MATCHED,
            "tool": "filesystem_access_denied",
            "reason": "unapproved_filesystem_delete_request"
        }


    if matches_note_edit_request(
        lowered
    ):

        return {
            "status": ROUTE_MATCHED,
            "tool": "edit_note",
            "reason": "clear_note_edit_request"
        }


    if matches_ambiguous_note_edit_request(
        lowered
    ):

        return {
            "status": ROUTE_AMBIGUOUS,
            "tool": None,
            "reason": "ambiguous_note_edit_request"
        }


    # note: Exact task completion is state-changing and must be
    # routed before general task listing/search behavior.
    if matches_task_completion_request(
        lowered
    ):

        return {
            "status": ROUTE_MATCHED,
            "tool": "complete_task",
            "reason": "clear_task_completion_request"
        }


    if matches_ambiguous_task_completion_request(
        lowered
    ):

        return {
            "status": ROUTE_AMBIGUOUS,
            "tool": None,
            "reason": "ambiguous_task_completion_request"
        }


    if matches_note_read_request(
        lowered
    ):

        return {
            "status": ROUTE_MATCHED,
            "tool": "read_note",
            "reason": "clear_note_read_request"
        }


    if matches_note_search_request(
        lowered
    ):

        return {
            "status": ROUTE_MATCHED,
            "tool": "search_notes",
            "reason": "clear_note_search_request"
        }


    if matches_ambiguous_note_search_request(
        lowered
    ):

        return {
            "status": ROUTE_AMBIGUOUS,
            "tool": None,
            "reason": "ambiguous_note_search_request"
        }


    if matches_note_listing_request(
        lowered
    ):

        return {
            "status": ROUTE_MATCHED,
            "tool": "list_notes",
            "reason": "clear_note_listing_request"
        }


    if matches_ambiguous_note_request(
        lowered
    ):

        return {
            "status": ROUTE_AMBIGUOUS,
            "tool": None,
            "reason": "ambiguous_note_request"
        }


    # note: Search-specific task routes are evaluated before
    # generic listing because some search phrasing begins with
    # "what tasks".
    if matches_task_search_request(
        lowered
    ):

        return {
            "status": ROUTE_MATCHED,
            "tool": "search_tasks",
            "reason": "clear_task_search_request"
        }


    if matches_ambiguous_task_search_request(
        lowered
    ):

        return {
            "status": ROUTE_AMBIGUOUS,
            "tool": None,
            "reason": "ambiguous_task_search_request"
        }


    # note: Supported status filters route to the safe-read
    # filter_tasks tool.
    if matches_task_filter_request(
        lowered
    ):

        return {
            "status": ROUTE_MATCHED,
            "tool": "filter_tasks",
            "reason": "clear_task_filter_request"
        }


    if matches_ambiguous_task_filter_request(
        lowered
    ):

        return {
            "status": ROUTE_AMBIGUOUS,
            "tool": None,
            "reason": "unsupported_task_status_filter"
        }


    if matches_task_listing_request(
        lowered
    ):

        return {
            "status": ROUTE_MATCHED,
            "tool": "list_tasks",
            "reason": "clear_task_listing_request"
        }


    if matches_ambiguous_task_request(
        lowered
    ):

        return {
            "status": ROUTE_AMBIGUOUS,
            "tool": None,
            "reason": "ambiguous_task_request"
        }


    if matches_confirmation_test_request(
        lowered
    ):

        return {
            "status": ROUTE_MATCHED,
            "tool": "test_confirmed_action",
            "reason": "confirmation_test_request"
        }


    if matches_blocked_test_request(
        lowered
    ):

        return {
            "status": ROUTE_MATCHED,
            "tool": "test_blocked_action",
            "reason": "blocked_test_request"
        }


    if matches_unapproved_filesystem_request(
        lowered
    ):

        return {
            "status": ROUTE_MATCHED,
            "tool": "filesystem_access_denied",
            "reason": "unapproved_filesystem_request"
        }


    return {
        "status": ROUTE_NO_MATCH,
        "tool": None,
        "reason": "no_supported_tool_match"
    }


# note: Preserve the original select_tool interface used by
# agent.py while benefiting from richer classification.
def select_tool(
    question
):

    """Return a tool only when routing confidence is sufficient."""

    classification = classify_tool_request(
        question
    )


    if classification.get(
        "status"
    ) == ROUTE_MATCHED:

        return classification.get(
            "tool"
        )


    return None
