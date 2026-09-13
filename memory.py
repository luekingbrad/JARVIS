# note: Import the tools needed to store and retrieve local memory.
from pathlib import Path
import json
import re


# note: Define where JARVIS's persistent memory is stored.
MEMORY_FILE = Path("memory/memory.json")


# note: Load JARVIS's persistent memory from the local JSON file.
def load_memory():

    """Load persistent JARVIS memory."""

    if not MEMORY_FILE.exists():
        return {"memories": []}

    with open(
        MEMORY_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# note: Save JARVIS's persistent memory back to the local JSON file.
def save_memory(memory):

    """Save persistent JARVIS memory."""

    MEMORY_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        MEMORY_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            memory,
            file,
            indent=4
        )


# note: Determine what category best describes a new memory.
def categorize_memory(text):

    """Determine the category of a memory."""

    lowered = text.lower()

    # note: Statements describing how JARVIS should operate
    # are classified as instructions.
    if any(
        phrase in lowered
        for phrase in [
            "should",
            "must",
            "always",
            "never",
            "do not",
            "don't"
        ]
    ):

        return "instruction"

    # note: Statements describing the user's preferences
    # are classified as preferences.
    if any(
        phrase in lowered
        for phrase in [
            "i prefer",
            "i like",
            "i dislike",
            "i don't like",
            "my preference",
            "i would prefer"
        ]
    ):

        return "preference"

    # note: Statements containing personal information about
    # the user are classified as user information.
    if any(
        phrase in lowered
        for phrase in [
            "my favorite",
            "my name",
            "i am",
            "i'm",
            "i have",
            "i work",
            "i live",
            "my job",
            "my birthday"
        ]
    ):

        return "user_information"

    # note: Statements describing future objectives are
    # classified as goals.
    if any(
        phrase in lowered
        for phrase in [
            "goal",
            "want to",
            "trying to",
            "plan to"
        ]
    ):

        return "goal"

    # note: Statements referring to ongoing work are
    # classified as projects.
    if any(
        phrase in lowered
        for phrase in [
            "project",
            "building",
            "working on"
        ]
    ):

        return "project"

    # note: Anything that does not match a more specific
    # category is stored as general information.
    return "general"


# note: Normalize memory text so small differences in capitalization
# or punctuation do not create duplicate memories.
def normalize_memory_text(text):

    """Normalize memory text for comparison."""

    normalized = text.lower().strip()

    normalized = normalized.rstrip(
        ".!?"
    )

    normalized = re.sub(
        r"\s+",
        " ",
        normalized
    )

    return normalized


# note: Identify the subject represented by structured personal
# information so conflicting values can replace older memories.
def get_memory_identity(text):

    """Return a stable identity for certain types of memory."""

    normalized = normalize_memory_text(
        text
    )

    # note: Treat favorite-item memories as one value per subject.
    favorite_match = re.match(
        r"^my favorite (.+?) is (.+)$",
        normalized
    )

    if favorite_match:

        favorite_subject = favorite_match.group(
            1
        ).strip()

        return (
            f"user_information:favorite:"
            f"{favorite_subject}"
        )

    # note: Treat the user's name as one replaceable personal fact.
    if normalized.startswith(
        "my name is "
    ):

        return "user_information:name"

    # note: Treat the user's job as one replaceable personal fact.
    if normalized.startswith(
        "my job is "
    ):

        return "user_information:job"

    # note: Treat the user's birthday as one replaceable personal fact.
    if normalized.startswith(
        "my birthday is "
    ):

        return "user_information:birthday"

    # note: Return no identity when the memory does not represent
    # a structured fact that JARVIS currently knows how to replace.
    return None


# note: Add a new memory while preventing exact duplicates
# and replacing conflicting structured personal facts.
def add_memory(text):

    """Add, ignore, or update a persistent JARVIS memory."""

    memory_data = load_memory()

    memories = memory_data.get(
        "memories",
        []
    )

    normalized_new_text = normalize_memory_text(
        text
    )

    new_identity = get_memory_identity(
        text
    )

    # note: Check whether this exact information is already stored.
    for stored_memory in memories:

        if isinstance(
            stored_memory,
            dict
        ):

            stored_text = stored_memory.get(
                "text",
                ""
            )

        else:

            stored_text = str(
                stored_memory
            )

        if normalize_memory_text(
            stored_text
        ) == normalized_new_text:

            return {
                "action": "duplicate",
                "memory": stored_memory
            }

    # note: Replace an older value when the new memory represents
    # the same structured personal fact.
    if new_identity:

        for index, stored_memory in enumerate(
            memories
        ):

            if isinstance(
                stored_memory,
                dict
            ):

                stored_text = stored_memory.get(
                    "text",
                    ""
                )

            else:

                stored_text = str(
                    stored_memory
                )

            stored_identity = get_memory_identity(
                stored_text
            )

            if stored_identity == new_identity:

                previous_memory = stored_memory

                updated_memory = {
                    "text": text,
                    "category": categorize_memory(
                        text
                    )
                }

                memories[index] = updated_memory

                save_memory(
                    memory_data
                )

                return {
                    "action": "updated",
                    "memory": updated_memory,
                    "previous_memory": previous_memory
                }

    # note: Store the information normally when it is genuinely new.
    new_memory = {
        "text": text,
        "category": categorize_memory(
            text
        )
    }

    memories.append(
        new_memory
    )

    save_memory(
        memory_data
    )

    return {
        "action": "added",
        "memory": new_memory
    }


# note: Return every memory currently stored by JARVIS.
def get_memories():

    """Return all stored memories."""

    memory = load_memory()

    return memory.get(
        "memories",
        []
    )


# note: Return only memories belonging to a specific category.
def get_memories_by_category(category):

    """Return memories belonging to a specific category."""

    memories = get_memories()

    matching_memories = []

    for memory in memories:

        if isinstance(
            memory,
            dict
        ):

            if memory.get(
                "category"
            ) == category:

                matching_memories.append(
                    memory
                )

    return matching_memories


# note: Break text into meaningful words so JARVIS can compare
# a user's question against stored memories.
def _get_keywords(text):

    words = re.findall(
        r"\b[a-zA-Z]{3,}\b",
        text.lower()
    )

    ignored_words = {
        "the",
        "and",
        "for",
        "are",
        "what",
        "does",
        "how",
        "did",
        "you",
        "your",
        "about",
        "with",
        "that",
        "this",
        "should",
        "would",
        "could",
        "tell",
        "remember",
        "from",
        "have",
        "when",
        "where",
        "which",
        "something",
        "anything",
        "favorite"
    }

    return {
        word
        for word in words
        if word not in ignored_words
    }


# note: Retrieve memories that share meaningful keywords
# with the user's current question.
def retrieve_relevant_memories(
    question,
    minimum_score=1
):

    """Return memories relevant to the current question."""

    memories = get_memories()

    question_keywords = _get_keywords(
        question
    )

    relevant_memories = []

    for memory in memories:

        if isinstance(
            memory,
            dict
        ):

            memory_text = memory.get(
                "text",
                ""
            )

        else:

            memory_text = memory

        memory_keywords = _get_keywords(
            memory_text
        )

        matches = question_keywords.intersection(
            memory_keywords
        )

        score = len(
            matches
        )

        if score >= minimum_score:

            relevant_memories.append(
                {
                    "memory": memory,
                    "score": score,
                    "matches": matches
                }
            )

    # note: Return the strongest memory matches first.
    relevant_memories.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return relevant_memories


# note: Detect whether the user is explicitly asking JARVIS
# to remember something.
def is_memory_request(question):

    """Determine whether the request asks JARVIS to remember something."""

    lowered = question.lower().strip()

    memory_phrases = [
        "remember that",
        "remember this",
        "remember my",
        "remember i ",
        "remember i'm",
        "remember i am"
    ]

    return any(
        phrase in lowered
        for phrase in memory_phrases
    )


# note: Extract the actual information the user wants JARVIS
# to remember.
def extract_memory_text(question):

    """Extract the memory text from a remember request."""

    text = question.strip()

    prefixes = [
        "remember that ",
        "remember this: ",
        "remember my ",
        "remember i ",
        "remember i'm ",
        "remember i am "
    ]

    lowered = text.lower()

    for prefix in prefixes:

        if lowered.startswith(prefix):

            extracted = text[
                len(prefix):
            ]

            if prefix == "remember my ":

                extracted = "my " + extracted

            elif prefix in [
                "remember i ",
                "remember i'm ",
                "remember i am "
            ]:

                extracted = "I " + extracted

            return extracted.strip()

    return text


# note: Find stored memories that match a piece of text
# using the same keyword system used by memory retrieval.
def find_matching_memories(
    search_text,
    minimum_score=1
):

    """Find stored memories matching the supplied text."""

    memories = get_memories()

    search_keywords = _get_keywords(
        search_text
    )

    matching_memories = []

    for index, memory in enumerate(
        memories
    ):

        if isinstance(
            memory,
            dict
        ):

            memory_text = memory.get(
                "text",
                ""
            )

        else:

            memory_text = str(
                memory
            )

        memory_keywords = _get_keywords(
            memory_text
        )

        matches = search_keywords.intersection(
            memory_keywords
        )

        score = len(
            matches
        )

        if score >= minimum_score:

            matching_memories.append(
                {
                    "index": index,
                    "memory": memory,
                    "score": score,
                    "matches": matches
                }
            )

    # note: Return the strongest memory matches first.
    matching_memories.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return matching_memories


# note: Remove one specific stored memory using its exact text.
def remove_memory(memory_text):

    """Remove a stored memory matching the supplied text."""

    memory_data = load_memory()

    memories = memory_data.get(
        "memories",
        []
    )

    target = memory_text.strip().lower()

    for index, memory in enumerate(
        memories
    ):

        if isinstance(
            memory,
            dict
        ):

            stored_text = memory.get(
                "text",
                ""
            )

        else:

            stored_text = str(
                memory
            )

        if stored_text.strip().lower() == target:

            removed_memory = memories.pop(
                index
            )

            save_memory(
                memory_data
            )

            return removed_memory

    return None


# note: Replace one existing memory with new information
# and automatically recalculate its category.
def update_memory(
    old_text,
    new_text
):

    """Replace an existing memory with new information."""

    memory_data = load_memory()

    memories = memory_data.get(
        "memories",
        []
    )

    target = old_text.strip().lower()

    for index, memory in enumerate(
        memories
    ):

        if isinstance(
            memory,
            dict
        ):

            stored_text = memory.get(
                "text",
                ""
            )

        else:

            stored_text = str(
                memory
            )

        if stored_text.strip().lower() == target:

            updated_memory = {
                "text": new_text,
                "category": categorize_memory(
                    new_text
                )
            }

            memories[index] = updated_memory

            save_memory(
                memory_data
            )

            return updated_memory

    return None


# note: Detect whether the user is explicitly asking JARVIS
# to forget a stored memory.
def is_forget_request(question):

    """Determine whether the user wants JARVIS to forget something."""

    lowered = question.lower().strip()

    forget_phrases = [
        "forget that ",
        "forget my ",
        "forget i ",
        "forget i'm ",
        "forget i am ",
        "forget "
    ]

    return any(
        lowered.startswith(phrase)
        for phrase in forget_phrases
    )


# note: Extract the information the user wants JARVIS
# to remove from persistent memory.
def extract_forget_text(question):

    """Extract the memory description from a forget request."""

    text = question.strip()

    lowered = text.lower()

    prefixes = [
        "forget that ",
        "forget my ",
        "forget i ",
        "forget i'm ",
        "forget i am ",
        "forget "
    ]

    for prefix in prefixes:

        if lowered.startswith(prefix):

            extracted = text[
                len(prefix):
            ]

            # note: Restore words removed as part of
            # recognizing the command prefix.
            if prefix == "forget my ":

                extracted = "my " + extracted

            elif prefix == "forget i ":

                extracted = "I " + extracted

            elif prefix == "forget i'm ":

                extracted = "I'm " + extracted

            elif prefix == "forget i am ":

                extracted = "I am " + extracted

            return extracted.strip()

    return text


# note: Detect whether the user is asking JARVIS to change
# information already stored in persistent memory.
def is_update_memory_request(question):

    """Determine whether the user wants to update a memory."""

    lowered = question.lower().strip()

    return (
        lowered.startswith("change ")
        or lowered.startswith("update ")
    ) and " to " in lowered


# note: Extract the memory subject and new value from a
# conversational change or update request.
def extract_update_memory_request(question):

    """Extract the subject and new value from an update request."""

    text = question.strip()

    # note: Remove trailing punctuation before parsing the request.
    text = text.rstrip(
        ".!?"
    )

    match = re.match(
        r"^(?:change|update)\s+(.+?)\s+to\s+(.+)$",
        text,
        re.IGNORECASE
    )

    if not match:

        return None

    subject = match.group(
        1
    ).strip()

    new_value = match.group(
        2
    ).strip()

    return {
        "subject": subject,
        "new_value": new_value
    }
