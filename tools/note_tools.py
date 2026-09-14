# note: Import tools for controlled filesystem access,
# timestamp generation, and JARVIS tool registration.
from pathlib import Path
from datetime import datetime
from tools.registry import register_tool


# note: Define the JARVIS project and approved notes directory
# so note tools cannot operate on arbitrary filesystem locations.
PROJECT_ROOT = Path(
    __file__
).resolve().parent.parent

NOTES_DIRECTORY = (
    PROJECT_ROOT
    / "notes"
)


# note: Limit note-search output so a broad query cannot return
# an excessive amount of content at once.
MAX_SEARCH_RESULTS = 10
MAX_EXCERPT_LENGTH = 160


# note: Create a new plain-text note only inside JARVIS's
# approved local notes directory.
def create_note(
    content
):

    """Create a controlled local JARVIS note."""

    if not isinstance(
        content,
        str
    ):

        raise ValueError(
            "Note content must be text."
        )


    cleaned_content = content.strip()


    if not cleaned_content:

        raise ValueError(
            "Note content cannot be empty."
        )


    NOTES_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True
    )


    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S_%f"
    )


    filename = (
        f"note_{timestamp}.txt"
    )


    note_path = (
        NOTES_DIRECTORY
        / filename
    )


    note_path.write_text(
        cleaned_content,
        encoding="utf-8"
    )


    return {
        "filename": filename,
        "path": str(
            note_path
        )
    }


# note: List only JARVIS-generated plain-text notes from the
# approved notes directory without exposing arbitrary files.
def list_notes():

    """List saved JARVIS notes."""

    if not NOTES_DIRECTORY.exists():

        return {
            "directory": str(
                NOTES_DIRECTORY
            ),
            "count": 0,
            "notes": []
        }


    if not NOTES_DIRECTORY.is_dir():

        raise ValueError(
            "The configured notes location is not a directory."
        )


    approved_directory = NOTES_DIRECTORY.resolve()


    notes = []


    for note_path in approved_directory.iterdir():

        if not note_path.is_file():

            continue


        if not note_path.name.startswith(
            "note_"
        ):

            continue


        if note_path.suffix.lower() != ".txt":

            continue


        notes.append(
            {
                "filename": note_path.name,
                "path": str(
                    note_path
                )
            }
        )


    notes.sort(
        key=lambda note: note[
            "filename"
        ],
        reverse=True
    )


    return {
        "directory": str(
            approved_directory
        ),
        "count": len(
            notes
        ),
        "notes": notes
    }


# note: Read one exact JARVIS-generated note while preventing
# path traversal and access outside the approved notes directory.
def read_note(
    filename
):

    """Read one controlled JARVIS note."""

    if not isinstance(
        filename,
        str
    ):

        raise ValueError(
            "Note filename must be text."
        )


    cleaned_filename = filename.strip()


    if not cleaned_filename:

        raise ValueError(
            "Note filename cannot be empty."
        )


    supplied_path = Path(
        cleaned_filename
    )


    if supplied_path.name != cleaned_filename:

        raise ValueError(
            "Only a note filename may be supplied."
        )


    if supplied_path.is_absolute():

        raise ValueError(
            "Absolute note paths are not allowed."
        )


    if (
        "/" in cleaned_filename
        or "\\" in cleaned_filename
    ):

        raise ValueError(
            "Note paths are not allowed."
        )


    if supplied_path.suffix.lower() != ".txt":

        raise ValueError(
            "Only plain-text JARVIS notes may be read."
        )


    if not cleaned_filename.startswith(
        "note_"
    ):

        raise ValueError(
            "Only JARVIS-generated notes may be read."
        )


    if not NOTES_DIRECTORY.exists():

        raise FileNotFoundError(
            "The JARVIS notes directory was not found."
        )


    if not NOTES_DIRECTORY.is_dir():

        raise ValueError(
            "The configured notes location is not a directory."
        )


    approved_directory = NOTES_DIRECTORY.resolve()


    note_path = (
        approved_directory
        / cleaned_filename
    )


    resolved_note_path = note_path.resolve()


    if resolved_note_path.parent != approved_directory:

        raise ValueError(
            "The requested note is outside the approved notes directory."
        )


    if not resolved_note_path.exists():

        raise FileNotFoundError(
            "The requested note was not found."
        )


    if not resolved_note_path.is_file():

        raise ValueError(
            "The requested note is not a file."
        )


    content = resolved_note_path.read_text(
        encoding="utf-8"
    ).strip()


    return {
        "filename": cleaned_filename,
        "path": str(
            resolved_note_path
        ),
        "content": content
    }


# note: Build a short bounded excerpt around a search match
# so note searches do not return entire note contents.
def create_search_excerpt(
    content,
    match_start,
    query_length
):

    """Create a compact excerpt around a search match."""

    half_window = (
        MAX_EXCERPT_LENGTH
        // 2
    )


    excerpt_start = max(
        0,
        match_start
        - half_window
    )


    excerpt_end = min(
        len(
            content
        ),
        match_start
        + query_length
        + half_window
    )


    excerpt = content[
        excerpt_start:excerpt_end
    ]


    excerpt = " ".join(
        excerpt.split()
    )


    if excerpt_start > 0:

        excerpt = (
            "..."
            + excerpt
        )


    if excerpt_end < len(
        content
    ):

        excerpt = (
            excerpt
            + "..."
        )


    return excerpt


# note: Search only JARVIS-generated plain-text notes inside
# the approved notes directory and return bounded excerpts.
def search_notes(
    query
):

    """Search saved JARVIS notes."""

    if not isinstance(
        query,
        str
    ):

        raise ValueError(
            "Search query must be text."
        )


    cleaned_query = query.strip()


    if not cleaned_query:

        raise ValueError(
            "Search query cannot be empty."
        )


    if not NOTES_DIRECTORY.exists():

        return {
            "query": cleaned_query,
            "count": 0,
            "matches": []
        }


    if not NOTES_DIRECTORY.is_dir():

        raise ValueError(
            "The configured notes location is not a directory."
        )


    approved_directory = NOTES_DIRECTORY.resolve()


    note_paths = []


    for note_path in approved_directory.iterdir():

        if not note_path.is_file():

            continue


        if not note_path.name.startswith(
            "note_"
        ):

            continue


        if note_path.suffix.lower() != ".txt":

            continue


        note_paths.append(
            note_path
        )


    note_paths.sort(
        key=lambda path: path.name,
        reverse=True
    )


    lowered_query = cleaned_query.lower()

    matches = []


    for note_path in note_paths:

        try:

            content = note_path.read_text(
                encoding="utf-8"
            )


        except (
            OSError,
            UnicodeError
        ):

            continue


        lowered_content = content.lower()


        match_start = lowered_content.find(
            lowered_query
        )


        if match_start == -1:

            continue


        excerpt = create_search_excerpt(
            content,
            match_start,
            len(
                cleaned_query
            )
        )


        matches.append(
            {
                "filename": note_path.name,
                "excerpt": excerpt
            }
        )


        if len(
            matches
        ) >= MAX_SEARCH_RESULTS:

            break


    return {
        "query": cleaned_query,
        "count": len(
            matches
        ),
        "matches": matches
    }


# note: Replace the complete contents of one exact JARVIS-generated
# note while preventing edits outside the approved notes directory.
def edit_note(
    filename,
    content
):

    """Edit one controlled JARVIS note."""

    if not isinstance(
        filename,
        str
    ):

        raise ValueError(
            "Note filename must be text."
        )


    cleaned_filename = filename.strip()


    if not cleaned_filename:

        raise ValueError(
            "Note filename cannot be empty."
        )


    supplied_path = Path(
        cleaned_filename
    )


    if supplied_path.name != cleaned_filename:

        raise ValueError(
            "Only a note filename may be supplied."
        )


    if supplied_path.is_absolute():

        raise ValueError(
            "Absolute note paths are not allowed."
        )


    if (
        "/" in cleaned_filename
        or "\\" in cleaned_filename
    ):

        raise ValueError(
            "Note paths are not allowed."
        )


    if supplied_path.suffix.lower() != ".txt":

        raise ValueError(
            "Only plain-text JARVIS notes may be edited."
        )


    if not cleaned_filename.startswith(
        "note_"
    ):

        raise ValueError(
            "Only JARVIS-generated notes may be edited."
        )


    if not isinstance(
        content,
        str
    ):

        raise ValueError(
            "Replacement note content must be text."
        )


    cleaned_content = content.strip()


    if not cleaned_content:

        raise ValueError(
            "Replacement note content cannot be empty."
        )


    if not NOTES_DIRECTORY.exists():

        raise FileNotFoundError(
            "The JARVIS notes directory was not found."
        )


    if not NOTES_DIRECTORY.is_dir():

        raise ValueError(
            "The configured notes location is not a directory."
        )


    approved_directory = NOTES_DIRECTORY.resolve()


    note_path = (
        approved_directory
        / cleaned_filename
    )


    resolved_note_path = note_path.resolve()


    if resolved_note_path.parent != approved_directory:

        raise ValueError(
            "The requested note is outside the approved notes directory."
        )


    if not resolved_note_path.exists():

        raise FileNotFoundError(
            "The requested note was not found."
        )


    if not resolved_note_path.is_file():

        raise ValueError(
            "The requested note is not a file."
        )


    resolved_note_path.write_text(
        cleaned_content,
        encoding="utf-8"
    )


    return {
        "filename": cleaned_filename,
        "path": str(
            resolved_note_path
        ),
        "content": cleaned_content
    }


# note: Permanently remove one exact JARVIS-generated note
# while preventing deletion outside the approved notes directory.
def delete_note(
    filename
):

    """Delete one controlled JARVIS note."""

    if not isinstance(
        filename,
        str
    ):

        raise ValueError(
            "Note filename must be text."
        )


    cleaned_filename = filename.strip()


    if not cleaned_filename:

        raise ValueError(
            "Note filename cannot be empty."
        )


    supplied_path = Path(
        cleaned_filename
    )


    if supplied_path.name != cleaned_filename:

        raise ValueError(
            "Only a note filename may be supplied."
        )


    if supplied_path.is_absolute():

        raise ValueError(
            "Absolute note paths are not allowed."
        )


    if (
        "/" in cleaned_filename
        or "\\" in cleaned_filename
    ):

        raise ValueError(
            "Note paths are not allowed."
        )


    if supplied_path.suffix.lower() != ".txt":

        raise ValueError(
            "Only plain-text JARVIS notes may be deleted."
        )


    if not cleaned_filename.startswith(
        "note_"
    ):

        raise ValueError(
            "Only JARVIS-generated notes may be deleted."
        )


    if not NOTES_DIRECTORY.exists():

        raise FileNotFoundError(
            "The JARVIS notes directory was not found."
        )


    if not NOTES_DIRECTORY.is_dir():

        raise ValueError(
            "The configured notes location is not a directory."
        )


    approved_directory = NOTES_DIRECTORY.resolve()


    note_path = (
        approved_directory
        / cleaned_filename
    )


    resolved_note_path = note_path.resolve()


    if resolved_note_path.parent != approved_directory:

        raise ValueError(
            "The requested note is outside the approved notes directory."
        )


    if not resolved_note_path.exists():

        raise FileNotFoundError(
            "The requested note was not found."
        )


    if not resolved_note_path.is_file():

        raise ValueError(
            "The requested note is not a file."
        )


    deleted_path = str(
        resolved_note_path
    )


    resolved_note_path.unlink()


    return {
        "filename": cleaned_filename,
        "path": deleted_path
    }


# note: Register controlled note creation as a write action
# that always requires explicit user confirmation.
register_tool(
    name="create_note",
    description=(
        "Create a new plain-text note inside "
        "JARVIS's approved notes directory."
    ),
    permission_level="confirm_required",
    function=create_note
)


# note: Register note listing as a safe read-only action.
register_tool(
    name="list_notes",
    description=(
        "List saved plain-text JARVIS notes."
    ),
    permission_level="safe_read",
    function=list_notes
)


# note: Register exact note reading as a safe read-only action.
register_tool(
    name="read_note",
    description=(
        "Read one exact saved plain-text JARVIS note."
    ),
    permission_level="safe_read",
    function=read_note
)


# note: Register note searching as a safe read-only action.
register_tool(
    name="search_notes",
    description=(
        "Search saved plain-text JARVIS notes "
        "for a specific text query."
    ),
    permission_level="safe_read",
    function=search_notes
)


# note: Register note editing as a controlled write action
# that cannot execute without explicit user confirmation.
register_tool(
    name="edit_note",
    description=(
        "Replace the contents of one exact saved "
        "plain-text JARVIS note."
    ),
    permission_level="confirm_required",
    function=edit_note
)


# note: Register note deletion as a destructive action that
# cannot execute without explicit user confirmation.
register_tool(
    name="delete_note",
    description=(
        "Permanently delete one exact saved "
        "plain-text JARVIS note."
    ),
    permission_level="confirm_required",
    function=delete_note
)
