import re


# note: Define common words that should not contribute to
# lexical knowledge-retrieval scoring.
STOP_WORDS = {
    "a",
    "about",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "do",
    "does",
    "for",
    "from",
    "how",
    "in",
    "is",
    "it",
    "me",
    "of",
    "on",
    "or",
    "tell",
    "that",
    "the",
    "this",
    "to",
    "what",
    "which",
    "who",
    "why",
    "with",
}


# note: Map common user-intent words to section concepts so
# retrieval can recognize structurally relevant headings.
HEADING_INTENT_ALIASES = {
    "responsibilities": {
        "activities",
        "activity",
        "duties",
        "tasks"
    },
    "responsibility": {
        "activities",
        "activity",
        "duties",
        "tasks"
    },
    "duties": {
        "activities",
        "activity",
        "responsibilities",
        "responsibility"
    },
    "purpose": {
        "purpose"
    },
    "relationship": {
        "relationship"
    },
    "mapping": {
        "mapping"
    },
    "lifecycle": {
        "lifecycle"
    }
}


# note: Convert text into meaningful lowercase words for
# deterministic lexical matching.
def tokenize(text):
    """Convert text into meaningful lowercase words."""

    words = re.findall(
        r"\b[a-zA-Z0-9]+\b",
        text.lower()
    )

    return {
        word
        for word in words
        if word not in STOP_WORDS
    }


# note: Split one Markdown knowledge document into logical
# heading-based chunks while preserving source information.
def chunk_markdown(
    filename,
    content
):
    """
    Split a Markdown document into heading-based knowledge chunks.

    Each chunk preserves:
    - source filename
    - document title
    - section hierarchy
    - heading level
    - section content
    """

    chunks = []

    # note: Derive the knowledge domain from the first directory
    # component of the relative source filename.
    filename_parts = filename.split(
        "/"
    )

    if len(filename_parts) > 1:
        domain = filename_parts[
            0
        ]

    else:
        domain = "general"


    # note: Derive an optional source group from the second
    # directory component for more specific knowledge organization.
    if len(filename_parts) > 2:
        source_group = filename_parts[
            1
        ]

    elif len(filename_parts) > 1:
        source_group = domain

    else:
        source_group = "general"

    document_title = None
    heading_stack = {}
    current_heading = None
    current_heading_level = None
    current_lines = []

    lines = content.splitlines()

    # note: Finalize the currently collected section before
    # beginning a new Markdown heading.
    def finalize_chunk():

        if current_heading is None:
            return

        section_content = "\n".join(
            current_lines
        ).strip()

        if not section_content:
            return

        parent_headings = []

        for level in sorted(
            heading_stack
        ):

            if level < current_heading_level:

                parent_headings.append(
                    heading_stack[
                        level
                    ]
                )

        section_path_parts = (
            parent_headings
            + [
                current_heading
            ]
        )

        # note: Create a stable human-readable chunk identifier
        # from the source file and section hierarchy.
        chunk_id = (
            filename
            + "::"
            + " > ".join(
                section_path_parts
            )
        )

        chunks.append(
            {
                "chunk_id": chunk_id,
                "domain": domain,
                "source_group": source_group,
                "filename": filename,
                "document_title": document_title,
                "heading": current_heading,
                "heading_level": current_heading_level,
                "section_path": " > ".join(
                    section_path_parts
                ),
                "content": section_content
            }
        )

    # note: Walk through the Markdown document and start a new
    # chunk whenever a heading is encountered.
    for line in lines:

        heading_match = re.match(
            r"^(#{1,6})\s+(.+?)\s*$",
            line
        )

        if heading_match:

            finalize_chunk()

            heading_level = len(
                heading_match.group(
                    1
                )
            )

            heading_text = heading_match.group(
                2
            ).strip()

            current_lines = []

            if heading_level == 1:

                document_title = heading_text

            for level in list(
                heading_stack.keys()
            ):

                if level >= heading_level:

                    del heading_stack[
                        level
                    ]

            heading_stack[
                heading_level
            ] = heading_text

            current_heading = heading_text
            current_heading_level = heading_level

            continue

        if current_heading is not None:

            current_lines.append(
                line
            )

    # note: Preserve the final section because there is no
    # later heading available to trigger finalization.
    finalize_chunk()

    return chunks


# note: Retrieve the most relevant whole knowledge documents
# using the original lexical scoring behavior.
def retrieve_knowledge(
    question,
    knowledge,
    top_k=3
):
    """
    Find the knowledge files most relevant to the user's question.

    Matching words in the filename receive additional weight.
    """

    question_words = tokenize(
        question
    )

    results = []

    for filename, content in knowledge.items():

        knowledge_words = tokenize(
            content
        )

        filename_words = tokenize(
            filename
        )

        matching_words = question_words.intersection(
            knowledge_words
        )

        filename_matches = question_words.intersection(
            filename_words
        )

        content_score = len(
            matching_words
        )

        filename_bonus = len(
            filename_matches
        ) * 5

        total_score = (
            content_score
            + filename_bonus
        )

        if total_score > 0:

            results.append(
                {
                    "filename": filename,
                    "score": total_score,
                    "matches": matching_words,
                    "filename_matches": filename_matches
                }
            )

    results.sort(
        key=lambda result: result[
            "score"
        ],
        reverse=True
    )

    return results[
        :top_k
    ]


# note: Map common user-facing knowledge-domain names to their
# canonical JARVIS domain identifiers for deterministic selection.
KNOWN_DOMAIN_ALIASES = {
    "grcp": "grcp",
    "nist": "nist",
    "coursework": "coursework",
    "risk management": "risk_management",
    "risk_management": "risk_management"
}


# note: Identify the knowledge domains currently available from
# the top-level directory component of each knowledge source.
def get_available_domains(
    knowledge
):

    available_domains = set()

    for filename in knowledge:

        filename_parts = filename.split(
            "/"
        )

        if len(filename_parts) > 1:
            domain = filename_parts[
                0
            ].strip().lower()

        else:
            domain = "general"

        available_domains.add(
            domain
        )

    return available_domains


# note: Restrict retrieval when the user explicitly names a
# recognized knowledge domain, and fail closed when that domain
# is recognized but is not currently loaded.
def select_allowed_domains(
    question,
    knowledge
):

    available_domains = get_available_domains(
        knowledge
    )

    normalized_question = question.lower()

    requested_domains = set()

    # note: Detect explicitly named known domains without
    # assuming that every known domain is currently available.
    for alias, canonical_domain in KNOWN_DOMAIN_ALIASES.items():

        if re.search(
            rf"\b{re.escape(alias)}\b",
            normalized_question
        ):
            requested_domains.add(
                canonical_domain
            )

    # note: Also recognize dynamically loaded domain names so
    # newly imported domains work without requiring alias entries.
    for domain in available_domains:

        readable_domain = domain.replace(
            "_",
            " "
        )

        domain_patterns = {
            domain,
            readable_domain
        }

        for pattern in domain_patterns:

            if re.search(
                rf"\b{re.escape(pattern)}\b",
                normalized_question
            ):
                requested_domains.add(
                    domain
                )

                break

    # note: Preserve unrestricted retrieval when the user did
    # not explicitly request any recognized knowledge domain.
    if not requested_domains:
        return None

    # note: Fail closed when any explicitly requested recognized
    # domain is unavailable instead of substituting another source.
    if not requested_domains.issubset(
        available_domains
    ):
        return set()

    return requested_domains

# note: Retrieve relevant knowledge with optional deterministic
# domain restrictions controlled by Python.
def retrieve_knowledge_chunks(
    question,
    knowledge,
    top_k=5,
    allowed_domains=None
):
    """
    Find the knowledge chunks most relevant to the user's question.

    Chunk scoring uses deterministic lexical matching while
    preserving document and section provenance.
    """

    question_words = tokenize(
        question
    )

    # note: Normalize explicitly allowed domains for
    # case-insensitive deterministic domain filtering.
    normalized_allowed_domains = None

    if allowed_domains is not None:
        normalized_allowed_domains = {
            str(domain).strip().lower()
            for domain in allowed_domains
        }


    results = []

    for filename, content in knowledge.items():

        chunks = chunk_markdown(
            filename,
            content
        )

        filename_words = tokenize(
            filename
        )

        filename_matches = question_words.intersection(
            filename_words
        )

        for chunk in chunks:

            # note: Exclude knowledge outside explicitly allowed
            # domains before relevance scoring can consider it.
            if (
                normalized_allowed_domains is not None
                and chunk["domain"].lower()
                not in normalized_allowed_domains
            ):
                continue

            content_words = tokenize(
                chunk["content"]
            )

            heading_words = tokenize(
                chunk["heading"]
            )

            section_path_words = tokenize(
                chunk["section_path"]
            )

            content_matches = question_words.intersection(
                content_words
            )

            heading_matches = question_words.intersection(
                heading_words
            )

            # note: Recognize deterministic intent aliases that connect
            # common question wording with structurally relevant headings.
            heading_intent_matches = set()

            for question_word in question_words:

                aliases = HEADING_INTENT_ALIASES.get(
                    question_word,
                    set()
                )

                if aliases.intersection(
                    heading_words
                ):

                    heading_intent_matches.add(
                        question_word
                    )

            section_path_matches = question_words.intersection(
                section_path_words
            )

            content_score = len(
                content_matches
            )

            # note: Give direct heading and recognized intent matches
            # stronger weight because headings describe section topics.
            heading_bonus = (
                len(
                    heading_matches
                ) * 3
                + len(
                    heading_intent_matches
                ) * 3
            )

            # note: Allow direct content, heading, or recognized heading
            # intent evidence to support filename relevance.
            if (
                content_matches
                or heading_matches
                or heading_intent_matches
            ):

                filename_bonus = len(
                    filename_matches
                ) * 5

            else:

                filename_bonus = 0

            total_score = (
                content_score
                + heading_bonus
                + filename_bonus
            )

            # note: Require meaningful retrieval evidence before allowing
            # a chunk through. Intent aliases alone are not sufficient
            # because they may identify a section type without identifying
            # the actual subject the user is asking about.
            has_filename_support = (
                bool(filename_matches)
                and (
                    bool(content_matches)
                    or bool(heading_matches)
                    or bool(heading_intent_matches)
                )
            )

            has_direct_section_support = (
                bool(heading_matches)
                and bool(content_matches)
            )

            has_multiple_content_matches = (
                len(content_matches) >= 2
            )

            has_sufficient_evidence = (
                has_filename_support
                or has_direct_section_support
                or has_multiple_content_matches
            )

            if (
                total_score > 0
                and has_sufficient_evidence
            ):

                # note: Preserve chunk identity and domain metadata through
                # retrieval so later pipeline stages can use provenance and
                # domain-aware knowledge controls.
                results.append(
                    {
                        "chunk_id": chunk[
                            "chunk_id"
                        ],
                        "domain": chunk[
                            "domain"
                        ],
                        # note: Preserve the nested source group through
                        # retrieval so later pipeline stages retain provenance.
                        "source_group": chunk[
                            "source_group"
                        ],
                        "filename": chunk[
                            "filename"
                        ],
                        "document_title": chunk[
                            "document_title"
                        ],
                        "heading": chunk[
                            "heading"
                        ],
                        "heading_level": chunk[
                            "heading_level"
                        ],
                        "section_path": chunk[
                            "section_path"
                        ],
                        "content": chunk[
                            "content"
                        ],
                        "score": total_score,
                        "content_matches": content_matches,
                        "heading_matches": heading_matches,
                        "heading_intent_matches": heading_intent_matches,
                        "section_path_matches": section_path_matches,
                        "filename_matches": filename_matches
                    }
                )

    # note: Sort all relevant chunks by their raw relevance score
    # before applying source-diversity selection.
    results.sort(
        key=lambda result: result[
            "score"
        ],
        reverse=True
    )

    # note: Prefer source diversity during final selection so one
    # highly repetitive document does not crowd out other relevant
    # knowledge sources.
    selected_results = []
    selected_chunk_ids = set()
    selected_filenames = set()

    for result in results:

        if len(
            selected_results
        ) >= top_k:

            break

        if result[
            "filename"
        ] not in selected_filenames:

            selected_results.append(
                result
            )

            selected_chunk_ids.add(
                result[
                    "chunk_id"
                ]
            )

            selected_filenames.add(
                result[
                    "filename"
                ]
            )

    # note: Fill remaining result slots with the next highest-scoring
    # chunks after each relevant source has had a chance to contribute.
    for result in results:

        if len(
            selected_results
        ) >= top_k:

            break

        if result[
            "chunk_id"
        ] in selected_chunk_ids:

            continue

        selected_results.append(
            result
        )

        selected_chunk_ids.add(
            result[
                "chunk_id"
            ]
        )

    # note: Restore descending relevance order after diversity
    # selection so callers still receive highest-scoring chunks first.
    selected_results.sort(
        key=lambda result: result[
            "score"
        ],
        reverse=True
    )

    return selected_results
