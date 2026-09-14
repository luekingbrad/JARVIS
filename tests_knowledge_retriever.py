from pathlib import Path

from knowledge_retriever import chunk_markdown
from knowledge_retriever import retrieve_knowledge
from knowledge_retriever import retrieve_knowledge_chunks
from knowledge_retriever import select_allowed_domains
from knowledge_retriever import tokenize


# note: Load the current local Markdown knowledge base using the
# same relative-path structure used by JARVIS.
def load_test_knowledge():

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


# note: Track passing and failing checks without requiring an
# external testing framework.
passed = 0
failed = 0


# note: Record one regression-test result and display useful
# information when a check fails.
def check(
    name,
    condition,
    expected=None,
    actual=None
):

    global passed
    global failed

    if condition:

        passed += 1

        print(
            f"PASS: {name}"
        )

    else:

        failed += 1

        print(
            f"FAIL: {name}"
        )

        if expected is not None:

            print(
                f"  Expected: {expected}"
            )

        if actual is not None:

            print(
                f"  Actual:   {actual}"
            )


# note: Load the real current knowledge base once so these tests
# protect the behavior JARVIS is actually using.
knowledge = load_test_knowledge()


# note: Verify basic tokenization behavior and stop-word removal.
tokens = tokenize(
    "What are the responsibilities of Perform?"
)

check(
    "Tokenizer keeps meaningful words",
    tokens == {
        "responsibilities",
        "perform"
    },
    {
        "responsibilities",
        "perform"
    },
    tokens
)


# note: Verify tokenization is case-insensitive.
tokens = tokenize(
    "LEARN learn Learn"
)

check(
    "Tokenizer normalizes case",
    tokens == {
        "learn"
    },
    {
        "learn"
    },
    tokens
)


# note: Verify punctuation does not become part of a token.
tokens = tokenize(
    "Perform, Align, Review!"
)

check(
    "Tokenizer removes punctuation",
    tokens == {
        "perform",
        "align",
        "review"
    },
    {
        "perform",
        "align",
        "review"
    },
    tokens
)


# note: Verify the four-capabilities question keeps the
# current strongest source ordering.
results = retrieve_knowledge(
    "What are the four GRC capabilities?",
    knowledge
)

result_names = [
    result["filename"]
    for result in results
]

check(
    "Four GRC capabilities returns grc first",
    len(result_names) >= 1
    and result_names[0] == "grcp/grc.md",
    "grcp/grc.md",
    result_names
)


check(
    "Four GRC capabilities includes capability model",
    "grcp/capability_model.md" in result_names,
    True,
    result_names
)


# note: Verify filename weighting strongly identifies the
# dedicated Perform knowledge file.
results = retrieve_knowledge(
    "What are the responsibilities of Perform?",
    knowledge
)

result_names = [
    result["filename"]
    for result in results
]

check(
    "Perform responsibilities returns perform first",
    len(result_names) >= 1
    and result_names[0] == "grcp/perform.md",
    "grcp/perform.md",
    result_names
)


perform_result = next(
    (
        result
        for result in results
        if result["filename"] == "grcp/perform.md"
    ),
    None
)

check(
    "Perform filename match is recorded",
    perform_result is not None
    and "perform" in perform_result[
        "filename_matches"
    ],
    True,
    (
        None
        if perform_result is None
        else perform_result[
            "filename_matches"
        ]
    )
)


# note: Lock the current weak-match governance behavior so future
# scoring changes are intentional rather than accidental.
results = retrieve_knowledge(
    "Explain governance to me.",
    knowledge
)

result_names = [
    result["filename"]
    for result in results
]

check(
    "Governance returns three current matching sources",
    len(result_names) == 3,
    3,
    len(result_names)
)


governance_scores = [
    result["score"]
    for result in results
]

check(
    "Governance current matches are weak score-one results",
    governance_scores == [
        1,
        1,
        1
    ],
    [
        1,
        1,
        1
    ],
    governance_scores
)


# note: Verify filename weighting correctly prioritizes Learn.
results = retrieve_knowledge(
    "What does Learn do?",
    knowledge
)

result_names = [
    result["filename"]
    for result in results
]

check(
    "Learn question returns learn first",
    len(result_names) >= 1
    and result_names[0] == "grcp/learn.md",
    "grcp/learn.md",
    result_names
)


# note: Verify a multi-source request retrieves both named
# capability documents.
results = retrieve_knowledge(
    "Compare Learn and Align.",
    knowledge
)

result_names = [
    result["filename"]
    for result in results
]

check(
    "Compare Learn and Align includes learn",
    "grcp/learn.md" in result_names,
    True,
    result_names
)


check(
    "Compare Learn and Align includes align",
    "grcp/align.md" in result_names,
    True,
    result_names
)


check(
    "Compare Learn and Align ranks named files first",
    len(result_names) >= 2
    and set(
        result_names[:2]
    ) == {
        "grcp/learn.md",
        "grcp/align.md"
    },
    {
        "grcp/learn.md",
        "grcp/align.md"
    },
    result_names[:2]
)


# note: Verify completely unrelated questions fail closed when
# no lexical knowledge match exists.
results = retrieve_knowledge(
    "What is the capital of France?",
    knowledge
)

check(
    "Unrelated question returns no knowledge",
    results == [],
    [],
    results
)


# note: Verify top_k still limits the number of returned
# knowledge results.
results = retrieve_knowledge(
    "governance",
    knowledge,
    top_k=2
)

check(
    "top_k limits retrieval results",
    len(results) <= 2,
    "2 or fewer results",
    len(results)
)


# note: Verify an empty question does not retrieve knowledge.
results = retrieve_knowledge(
    "",
    knowledge
)

check(
    "Empty question returns no knowledge",
    results == [],
    [],
    results
)


# note: Verify a question containing only stop words does not
# produce false knowledge matches.
results = retrieve_knowledge(
    "What is this and how is it?",
    knowledge
)

check(
    "Stop-word-only question returns no knowledge",
    results == [],
    [],
    results
)


# note: Verify case differences in the user request do not
# change retrieval behavior.
lowercase_results = retrieve_knowledge(
    "what does perform do?",
    knowledge
)

uppercase_results = retrieve_knowledge(
    "WHAT DOES PERFORM DO?",
    knowledge
)

lowercase_names = [
    result["filename"]
    for result in lowercase_results
]

uppercase_names = [
    result["filename"]
    for result in uppercase_results
]

check(
    "Retrieval is case-insensitive",
    lowercase_names == uppercase_names,
    lowercase_names,
    uppercase_names
)


# note: Verify punctuation differences do not prevent a direct
# capability filename match.
results = retrieve_knowledge(
    "Perform?!",
    knowledge
)

result_names = [
    result["filename"]
    for result in results
]

check(
    "Punctuation does not block Perform retrieval",
    len(result_names) >= 1
    and result_names[0] == "grcp/perform.md",
    "grcp/perform.md",
    result_names
)


# note: Verify Review receives the same direct filename-weighting
# behavior as the other capability-specific files.
results = retrieve_knowledge(
    "What does Review do?",
    knowledge
)

result_names = [
    result["filename"]
    for result in results
]

check(
    "Review question returns review first",
    len(result_names) >= 1
    and result_names[0] == "grcp/review.md",
    "grcp/review.md",
    result_names
)


# note: Verify Align receives the same direct filename-weighting
# behavior as the other capability-specific files.
results = retrieve_knowledge(
    "What does Align do?",
    knowledge
)

result_names = [
    result["filename"]
    for result in results
]

check(
    "Align question returns align first",
    len(result_names) >= 1
    and result_names[0] == "grcp/align.md",
    "grcp/align.md",
    result_names
)


# note: Verify a three-capability request can retrieve all three
# specifically named capability files when top_k allows it.
results = retrieve_knowledge(
    "Compare Learn, Align, and Perform.",
    knowledge,
    top_k=3
)

result_names = [
    result["filename"]
    for result in results
]

check(
    "Three-capability comparison retrieves all named files",
    {
        "grcp/learn.md",
        "grcp/align.md",
        "grcp/perform.md"
    }.issubset(
        set(
            result_names
        )
    ),
    {
        "grcp/learn.md",
        "grcp/align.md",
        "grcp/perform.md"
    },
    result_names
)


# note: Lock the current exact-word limitation so future semantic
# retrieval improvements can be measured against this baseline.
results = retrieve_knowledge(
    "What duties belong to Perform?",
    knowledge
)

result_names = [
    result["filename"]
    for result in results
]

check(
    "Synonym request still finds Perform through filename match",
    len(result_names) >= 1
    and result_names[0] == "grcp/perform.md",
    "grcp/perform.md",
    result_names
)


# note: Document the current lexical limitation where an unrelated
# synonym without a known filename or content match retrieves nothing.
results = retrieve_knowledge(
    "Describe the duties involved.",
    knowledge
)

check(
    "Unsupported synonym-only request returns no knowledge",
    results == [],
    [],
    results
)


# note: Verify top_k equal to one returns at most one result.
results = retrieve_knowledge(
    "governance",
    knowledge,
    top_k=1
)

check(
    "top_k one returns one or fewer results",
    len(results) <= 1,
    "1 or fewer results",
    len(results)
)


# note: Verify retrieval results remain ordered from highest
# score to lowest score.
results = retrieve_knowledge(
    "What are the responsibilities of Perform?",
    knowledge
)

scores = [
    result["score"]
    for result in results
]

check(
    "Retrieval results are sorted by descending score",
    scores == sorted(
        scores,
        reverse=True
    ),
    sorted(
        scores,
        reverse=True
    ),
    scores
)


# note: Verify every returned result continues to contain the
# metadata fields expected by the current retrieval pipeline.
results = retrieve_knowledge(
    "What does Learn do?",
    knowledge
)

required_fields = {
    "filename",
    "score",
    "matches",
    "filename_matches"
}

metadata_valid = all(
    required_fields.issubset(
        result.keys()
    )
    for result in results
)

check(
    "Retrieval results preserve expected metadata fields",
    metadata_valid,
    True,
    metadata_valid
)


# note: Verify a zero top_k value safely returns no results.
results = retrieve_knowledge(
    "What does Perform do?",
    knowledge,
    top_k=0
)

check(
    "top_k zero returns no results",
    results == [],
    [],
    results
)


# note: Verify top_k larger than the knowledge base does not
# duplicate results or raise an error.
results = retrieve_knowledge(
    "governance",
    knowledge,
    top_k=100
)

result_names = [
    result["filename"]
    for result in results
]

check(
    "Large top_k does not duplicate knowledge files",
    len(result_names) == len(
        set(
            result_names
        )
    ),
    "unique filenames only",
    result_names
)


# note: Verify every returned result has a positive score because
# the current retriever excludes zero-score matches.
results = retrieve_knowledge(
    "governance",
    knowledge
)

positive_scores = all(
    result["score"] > 0
    for result in results
)

check(
    "Returned knowledge results always have positive scores",
    positive_scores,
    True,
    positive_scores
)


# note: Verify the current retriever does not return more results
# than the requested top_k value.
results = retrieve_knowledge(
    "Learn Align Perform Review governance capabilities",
    knowledge,
    top_k=3
)

check(
    "Retriever never exceeds requested top_k",
    len(results) <= 3,
    "3 or fewer results",
    len(results)
)


# note: Verify a query containing numbers can still be tokenized
# and processed without causing a retrieval error.
results = retrieve_knowledge(
    "What are the 4 GRC capabilities?",
    knowledge
)

result_names = [
    result["filename"]
    for result in results
]

check(
    "Numeric capability question retrieves GRC knowledge",
    len(result_names) >= 1,
    True,
    result_names
)


# note: Verify repeated words do not artificially increase the
# current score because tokenization uses a set.
single_results = retrieve_knowledge(
    "Perform",
    knowledge
)

repeated_results = retrieve_knowledge(
    "Perform Perform Perform",
    knowledge
)

single_scores = [
    (
        result["filename"],
        result["score"]
    )
    for result in single_results
]

repeated_scores = [
    (
        result["filename"],
        result["score"]
    )
    for result in repeated_results
]

check(
    "Repeated query words do not increase current scores",
    single_scores == repeated_scores,
    single_scores,
    repeated_scores
)


# note: Verify retrieval against an empty knowledge dictionary
# safely produces no results.
results = retrieve_knowledge(
    "What does Perform do?",
    {}
)

check(
    "Empty knowledge base returns no results",
    results == [],
    [],
    results
)


# note: Load a representative knowledge document so the
# Markdown chunking behavior can be regression tested.
capability_model_content = knowledge[
    "grcp/capability_model.md"
]

chunks = chunk_markdown(
    "grcp/capability_model.md",
    capability_model_content
)


# note: Verify the capability-model document currently produces
# the expected number of meaningful heading-based chunks.
check(
    "Capability model produces ten chunks",
    len(chunks) == 10,
    10,
    len(chunks)
)


# note: Verify every chunk preserves the original source
# filename for future provenance-aware retrieval.
chunk_sources_valid = all(
    chunk["filename"]
    == "grcp/capability_model.md"
    for chunk in chunks
)

check(
    "Chunks preserve source filename",
    chunk_sources_valid,
    True,
    chunk_sources_valid
)


# note: Verify every chunk preserves the top-level document title.
document_titles_valid = all(
    chunk["document_title"]
    == "GRCP Capability Model"
    for chunk in chunks
)

check(
    "Chunks preserve document title",
    document_titles_valid,
    True,
    document_titles_valid
)


# note: Verify ordinary second-level Markdown sections preserve
# their expected hierarchy.
perform_chunk = next(
    (
        chunk
        for chunk in chunks
        if chunk["heading"] == "Perform"
        and chunk["heading_level"] == 2
    ),
    None
)

check(
    "Perform chunk preserves section path",
    perform_chunk is not None
    and perform_chunk["section_path"]
    == "GRCP Capability Model > Perform",
    "GRCP Capability Model > Perform",
    (
        None
        if perform_chunk is None
        else perform_chunk["section_path"]
    )
)


# note: Verify nested third-level Markdown headings retain their
# parent section rather than being flattened.
governance_chunk = next(
    (
        chunk
        for chunk in chunks
        if chunk["heading"] == "Governance"
        and chunk["heading_level"] == 3
    ),
    None
)

expected_governance_path = (
    "GRCP Capability Model > "
    "Management, Governance, and Assurance > "
    "Governance"
)

check(
    "Nested Governance chunk preserves parent hierarchy",
    governance_chunk is not None
    and governance_chunk["section_path"]
    == expected_governance_path,
    expected_governance_path,
    (
        None
        if governance_chunk is None
        else governance_chunk["section_path"]
    )
)


# note: Verify the nested Governance chunk contains the actual
# knowledge from that subsection.
check(
    "Governance chunk preserves subsection content",
    governance_chunk is not None
    and "direction and oversight"
    in governance_chunk["content"],
    True,
    (
        None
        if governance_chunk is None
        else governance_chunk["content"]
    )
)


# note: Verify chunk content does not include Markdown heading
# syntax because heading metadata is stored separately.
heading_syntax_removed = all(
    not chunk["content"].lstrip().startswith(
        "#"
    )
    for chunk in chunks
)

check(
    "Chunk content excludes Markdown heading syntax",
    heading_syntax_removed,
    True,
    heading_syntax_removed
)


# note: Verify empty Markdown sections are not emitted as empty
# retrieval chunks.
empty_chunks_absent = all(
    chunk["content"].strip()
    for chunk in chunks
)

check(
    "Chunker excludes empty chunks",
    empty_chunks_absent,
    True,
    empty_chunks_absent
)


# note: Verify the chunker safely handles an empty document.
empty_document_chunks = chunk_markdown(
    "empty.md",
    ""
)

check(
    "Empty Markdown document produces no chunks",
    empty_document_chunks == [],
    [],
    empty_document_chunks
)


# note: Verify plain text without Markdown headings currently
# produces no heading-based chunks.
plain_text_chunks = chunk_markdown(
    "plain.md",
    "This document has no Markdown headings."
)

check(
    "Headingless document produces no chunks",
    plain_text_chunks == [],
    [],
    plain_text_chunks
)


# note: Verify a simple document with one title and one section
# produces one usable knowledge chunk.
simple_markdown = """
# Test Document

## Purpose

This is test knowledge.
"""

simple_chunks = chunk_markdown(
    "test.md",
    simple_markdown
)

check(
    "Simple Markdown document produces one section chunk",
    len(simple_chunks) == 1,
    1,
    len(simple_chunks)
)


check(
    "Simple chunk preserves section metadata",
    len(simple_chunks) == 1
    and simple_chunks[0]["section_path"]
    == "Test Document > Purpose",
    "Test Document > Purpose",
    (
        None
        if not simple_chunks
        else simple_chunks[0]["section_path"]
    )
)


# note: Verify chunk-level retrieval preserves provenance
# information needed by later knowledge-intelligence features.
results = retrieve_knowledge_chunks(
    "What does Perform do?",
    knowledge
)

required_chunk_fields = {
    "chunk_id",
    "domain",
    "filename",
    "document_title",
    "heading",
    "heading_level",
    "section_path",
    "content",
    "score",
    "content_matches",
    "heading_matches",
    "section_path_matches",
    "filename_matches"
}

chunk_metadata_valid = all(
    required_chunk_fields.issubset(
        result.keys()
    )
    for result in results
)

check(
    "Chunk retrieval preserves expected metadata",
    chunk_metadata_valid,
    True,
    chunk_metadata_valid
)


# note: Verify a direct Perform request retrieves knowledge
# from the dedicated Perform source.
results = retrieve_knowledge_chunks(
    "What does Perform do?",
    knowledge
)

result_sources = [
    result["filename"]
    for result in results
]

check(
    "Chunk retrieval finds Perform source",
    "grcp/perform.md" in result_sources,
    True,
    result_sources
)


# note: Verify filename matches cannot make unrelated sections
# relevant when the section itself contains no matching evidence.
results = retrieve_knowledge_chunks(
    "Perform",
    knowledge,
    top_k=20
)

unsupported_filename_only_chunks = [
    result
    for result in results
    if result["filename"] == "grcp/perform.md"
    and not result["content_matches"]
    and not result["heading_matches"]
]

check(
    "Filename match alone does not retrieve a chunk",
    unsupported_filename_only_chunks == [],
    [],
    unsupported_filename_only_chunks
)


# note: Verify chunk retrieval can return knowledge from more
# than one source for a multi-source comparison request.
results = retrieve_knowledge_chunks(
    "Compare Learn and Align.",
    knowledge,
    top_k=10
)

result_sources = {
    result["filename"]
    for result in results
}

check(
    "Chunk comparison retrieves Learn and Align sources",
    {
        "grcp/learn.md",
        "grcp/align.md"
    }.issubset(
        result_sources
    ),
    {
        "grcp/learn.md",
        "grcp/align.md"
    },
    result_sources
)


# note: Verify governance retrieval identifies actual
# governance-related sections rather than only whole documents.
results = retrieve_knowledge_chunks(
    "Explain governance to me.",
    knowledge
)

governance_sections = [
    result["section_path"]
    for result in results
]

check(
    "Governance retrieval returns governance sections",
    any(
        "Governance" in section
        for section in governance_sections
    ),
    True,
    governance_sections
)


# note: Verify unrelated requests still fail closed at the
# chunk-retrieval layer.
results = retrieve_knowledge_chunks(
    "What is the capital of France?",
    knowledge
)

check(
    "Unrelated chunk request returns no knowledge",
    results == [],
    [],
    results
)


# note: Verify chunk retrieval respects its requested top_k
# result limit.
results = retrieve_knowledge_chunks(
    "governance",
    knowledge,
    top_k=2
)

check(
    "Chunk retrieval respects top_k",
    len(results) <= 2,
    "2 or fewer results",
    len(results)
)


# note: Verify every returned chunk has a positive score.
results = retrieve_knowledge_chunks(
    "governance",
    knowledge,
    top_k=20
)

positive_chunk_scores = all(
    result["score"] > 0
    for result in results
)

check(
    "Chunk retrieval only returns positive scores",
    positive_chunk_scores,
    True,
    positive_chunk_scores
)


# note: Verify chunk results remain ordered from highest
# relevance score to lowest relevance score.
results = retrieve_knowledge_chunks(
    "What are the four GRC capabilities?",
    knowledge
)

chunk_scores = [
    result["score"]
    for result in results
]

check(
    "Chunk results are sorted by descending score",
    chunk_scores == sorted(
        chunk_scores,
        reverse=True
    ),
    sorted(
        chunk_scores,
        reverse=True
    ),
    chunk_scores
)


# note: Verify an empty knowledge base safely returns no
# chunk-level retrieval results.
results = retrieve_knowledge_chunks(
    "What does Perform do?",
    {}
)

check(
    "Empty knowledge base returns no chunks",
    results == [],
    [],
    results
)



# note: Verify retrieved chunks preserve the domain derived
# from their source directory.
results = retrieve_knowledge_chunks(
    "What does Perform do?",
    knowledge
)

perform_domain_valid = any(
    result["filename"] == "grcp/perform.md"
    and result["domain"] == "grcp"
    for result in results
)

check(
    "Retrieved chunks preserve knowledge domain",
    perform_domain_valid,
    True,
    perform_domain_valid
)


# note: Verify retrieved chunks preserve stable chunk IDs so
# specific knowledge sections can be identified later.
perform_chunk_ids_valid = all(
    result["chunk_id"].startswith(
        result["filename"] + "::"
    )
    for result in results
)

check(
    "Retrieved chunks preserve stable chunk IDs",
    perform_chunk_ids_valid,
    True,
    perform_chunk_ids_valid
)


# note: Verify source-diversity selection prevents one document
# from consuming the leading results in a comparison request.
results = retrieve_knowledge_chunks(
    "Compare Learn and Align.",
    knowledge,
    top_k=5
)

leading_sources = [
    result["filename"]
    for result in results[:2]
]

comparison_diversity_valid = (
    "grcp/learn.md" in leading_sources
    and "grcp/align.md" in leading_sources
)

check(
    "Comparison results preserve source diversity",
    comparison_diversity_valid,
    True,
    leading_sources
)


# note: Verify an intent alias by itself is not enough to
# identify knowledge when the requested subject is ambiguous.
results = retrieve_knowledge_chunks(
    "What are the duties involved?",
    knowledge
)

check(
    "Intent-only ambiguous request fails closed",
    results == [],
    [],
    results
)


# note: Verify a vague unsupported knowledge request does not
# pass retrieval without meaningful lexical evidence.
results = retrieve_knowledge_chunks(
    "What does the framework say?",
    knowledge
)

check(
    "Vague unsupported request fails closed",
    results == [],
    [],
    results
)


# note: Verify multiple direct content matches can preserve a
# useful low-score chunk without requiring filename support.
results = retrieve_knowledge_chunks(
    "What are the four GRC capabilities?",
    knowledge,
    top_k=10
)

capability_overview_found = any(
    result["filename"] == "grcp/capability_model.md"
    and result["heading"] == "Overview"
    and {
        "capabilities",
        "four"
    }.issubset(
        result["content_matches"]
    )
    for result in results
)

check(
    "Multiple content matches preserve low-score knowledge",
    capability_overview_found,
    True,
    capability_overview_found
)


# note: Verify filename evidence can establish the requested
# subject while a heading-intent match identifies the section.
results = retrieve_knowledge_chunks(
    "What are the responsibilities of Perform?",
    knowledge
)

perform_activities_found = any(
    result["filename"] == "grcp/perform.md"
    and result["heading"] == "Key Activities"
    and "perform" in result["filename_matches"]
    and "responsibilities" in result["heading_intent_matches"]
    for result in results
)

check(
    "Filename plus intent evidence preserves Perform activities",
    perform_activities_found,
    True,
    perform_activities_found
)


# note: Verify direct heading and content agreement remains
# sufficient evidence for concept-focused knowledge retrieval.
results = retrieve_knowledge_chunks(
    "Explain governance to me.",
    knowledge
)

direct_governance_found = any(
    "governance" in result["heading_matches"]
    and "governance" in result["content_matches"]
    for result in results
)

check(
    "Direct heading and content evidence remains valid",
    direct_governance_found,
    True,
    direct_governance_found
)


# note: Verify conversational filler words do not contribute
# lexical evidence during knowledge retrieval.
filler_tokens = tokenize(
    "Tell me about management."
)

check(
    "Tokenizer removes conversational filler",
    filler_tokens,
    {"management"},
    filler_tokens
)


# note: Verify removing conversational filler does not prevent
# a legitimate management concept request from retrieving knowledge.
results = retrieve_knowledge_chunks(
    "Tell me about management.",
    knowledge
)

management_found = any(
    "management" in result["content_matches"]
    or "management" in result["heading_matches"]
    for result in results
)

check(
    "Management request survives filler removal",
    management_found,
    True,
    management_found
)


# note: Verify comparison requests preserve evidence for both
# concepts instead of allowing one source to crowd out the other.
results = retrieve_knowledge_chunks(
    "How are Learn and Align different?",
    knowledge
)

comparison_sources = {
    result["filename"]
    for result in results
}

comparison_has_both_sources = (
    "grcp/learn.md" in comparison_sources
    and "grcp/align.md" in comparison_sources
)

check(
    "Learn and Align comparison preserves both sources",
    comparison_has_both_sources,
    True,
    comparison_sources
)


# note: Verify lifecycle questions retrieve evidence spanning
# multiple GRCP sources needed for multi-source synthesis.
results = retrieve_knowledge_chunks(
    "How do Learn, Align, Perform, and Review work together?",
    knowledge
)

lifecycle_sources = {
    result["filename"]
    for result in results
}

required_lifecycle_sources = {
    "grcp/learn.md",
    "grcp/align.md",
    "grcp/perform.md",
    "grcp/review.md"
}

lifecycle_has_multiple_sources = (
    len(
        lifecycle_sources.intersection(
            required_lifecycle_sources
        )
    ) >= 3
)

check(
    "Lifecycle request preserves multi-source evidence",
    lifecycle_has_multiple_sources,
    True,
    lifecycle_sources
)


# note: Create a small in-memory knowledge set with intentionally
# conflicting statements so conflict handling can be tested safely.
conflicting_knowledge = {
    "test/source_a.md": """
# Control Testing

## Frequency

Control testing is performed annually.
""",
    "test/source_b.md": """
# Control Testing

## Frequency

Control testing is performed quarterly.
"""
}


# note: Verify retrieval preserves both conflicting sources instead
# of allowing one source to silently replace the other.
results = retrieve_knowledge_chunks(
    "How often is control testing performed?",
    conflicting_knowledge
)

conflict_sources = {
    result["filename"]
    for result in results
}

conflict_preserves_both_sources = (
    "test/source_a.md" in conflict_sources
    and "test/source_b.md" in conflict_sources
)

check(
    "Conflicting knowledge preserves both sources",
    conflict_preserves_both_sources,
    True,
    conflict_sources
)


# note: Verify the conflicting statements themselves remain available
# so a later reasoning layer can recognize and report disagreement.
conflict_contents = {
    result["content"].strip()
    for result in results
}

conflicting_statements_preserved = (
    any(
        "annually" in content.lower()
        for content in conflict_contents
    )
    and any(
        "quarterly" in content.lower()
        for content in conflict_contents
    )
)

check(
    "Conflicting statements remain available for reasoning",
    conflicting_statements_preserved,
    True,
    conflict_contents
)


# note: Verify nested knowledge paths preserve both the top-level
# domain and the more specific second-level source group.
nested_chunks = chunk_markdown(
    "coursework/core_400/systems_thinking.md",
    """
# Systems Thinking

## Purpose

Systems thinking examines relationships across a system.
"""
)

nested_metadata_valid = (
    len(nested_chunks) == 1
    and nested_chunks[0]["domain"] == "coursework"
    and nested_chunks[0]["source_group"] == "core_400"
)

check(
    "Nested knowledge preserves source group metadata",
    nested_metadata_valid,
    True,
    nested_chunks
)


# note: Verify nested source-group metadata survives retrieval
# so the live JARVIS pipeline can safely use that provenance.
nested_retrieval_knowledge = {
    "coursework/cyber_resilience/recovery_planning.md": """
# Cyber Resilience Test

## Recovery Planning

A resilient system should prepare for disruption by defining
recovery priorities, maintaining critical capabilities, and
supporting restoration after an adverse event.
"""
}

nested_retrieval_results = retrieve_knowledge_chunks(
    "What does recovery planning involve?",
    nested_retrieval_knowledge
)

source_group_preserved = (
    len(nested_retrieval_results) > 0
    and nested_retrieval_results[0]["domain"]
    == "coursework"
    and nested_retrieval_results[0]["source_group"]
    == "cyber_resilience"
)

check(
    "Nested source group survives retrieval",
    source_group_preserved,
    True,
    nested_retrieval_results
)


# note: Create a small multi-domain knowledge set so domain
# restrictions can be tested independently of the real knowledge base.
domain_control_knowledge = {
    "grcp/perform.md": """
# Perform

## Purpose

Perform executes actions, controls, and activities needed
to achieve objectives and manage risk.
""",
    "nist/resilience.md": """
# Cyber Resilience

## Purpose

Cyber resilience supports the ability to anticipate,
withstand, recover from, and adapt to adverse conditions.
"""
}


# note: Verify a single allowed domain prevents retrieval
# from all other knowledge domains.
results = retrieve_knowledge_chunks(
    "What is Perform?",
    domain_control_knowledge,
    allowed_domains={
        "grcp"
    }
)

single_domain_valid = (
    len(results) > 0
    and all(
        result["domain"] == "grcp"
        for result in results
    )
)

check(
    "Single allowed domain restricts retrieval",
    single_domain_valid,
    True,
    results
)


# note: Verify multiple explicitly allowed domains can both
# participate in retrieval when relevant.
results = retrieve_knowledge_chunks(
    "How do Perform and cyber resilience relate?",
    domain_control_knowledge,
    allowed_domains={
        "grcp",
        "nist"
    }
)

multi_domain_results = {
    result["domain"]
    for result in results
}

multi_domain_valid = (
    "grcp" in multi_domain_results
    and "nist" in multi_domain_results
)

check(
    "Multiple allowed domains can participate",
    multi_domain_valid,
    True,
    multi_domain_results
)


# note: Verify a relevant knowledge source cannot be retrieved
# when its domain is not explicitly allowed.
results = retrieve_knowledge_chunks(
    "What is Perform?",
    domain_control_knowledge,
    allowed_domains={
        "nist"
    }
)

blocked_domain_valid = (
    len(results) == 0
)

check(
    "Blocked domain cannot be retrieved",
    blocked_domain_valid,
    True,
    results
)


# note: Verify an explicitly empty allowed-domain set fails
# closed and permits no knowledge retrieval.
results = retrieve_knowledge_chunks(
    "What is Perform?",
    domain_control_knowledge,
    allowed_domains=set()
)

empty_domain_valid = (
    len(results) == 0
)

check(
    "Empty allowed-domain set fails closed",
    empty_domain_valid,
    True,
    results
)


# note: Create a small knowledge set with several domains so
# deterministic domain selection can be tested in isolation.
domain_selection_knowledge = {
    "grcp/perform.md": """
# Perform

## Purpose

Perform executes actions and controls.
""",
    "coursework/core_400/systems_thinking.md": """
# Systems Thinking

## Purpose

Systems thinking examines relationships across a system.
""",
    "risk_management/framework.md": """
# Risk Management

## Purpose

Risk management supports objective achievement.
"""
}


# note: Verify an explicitly named loaded domain is selected.
selected_domains = select_allowed_domains(
    "What does GRCP say about Perform?",
    domain_selection_knowledge
)

check(
    "Explicit GRCP domain is selected",
    selected_domains == {"grcp"},
    {"grcp"},
    selected_domains
)


# note: Verify underscore-based domain names can also be
# recognized when the user writes them with normal spaces.
selected_domains = select_allowed_domains(
    "Explain risk management.",
    domain_selection_knowledge
)

check(
    "Readable risk management domain is selected",
    selected_domains == {"risk_management"},
    {"risk_management"},
    selected_domains
)


# note: Verify nested source groups do not replace the actual
# top-level domain during domain selection.
selected_domains = select_allowed_domains(
    "Use the coursework knowledge for this.",
    domain_selection_knowledge
)

check(
    "Coursework top-level domain is selected",
    selected_domains == {"coursework"},
    {"coursework"},
    selected_domains
)


# note: Verify multiple explicitly named loaded domains can
# be selected together for cross-domain retrieval.
selected_domains = select_allowed_domains(
    "Compare GRCP with risk management.",
    domain_selection_knowledge
)

check(
    "Multiple explicit domains are selected",
    selected_domains == {
        "grcp",
        "risk_management"
    },
    {
        "grcp",
        "risk_management"
    },
    selected_domains
)


# note: Verify ordinary questions that do not explicitly name
# a loaded domain preserve unrestricted retrieval behavior.
selected_domains = select_allowed_domains(
    "What are the responsibilities of Perform?",
    domain_selection_knowledge
)

check(
    "Unnamed domain preserves unrestricted retrieval",
    selected_domains is None,
    None,
    selected_domains
)


# note: Verify an explicitly requested recognized domain that
# is not loaded fails closed instead of falling back to other knowledge.
selected_domains = select_allowed_domains(
    "Use the NIST domain for this answer.",
    domain_selection_knowledge
)

check(
    "Unavailable explicit domain fails closed",
    selected_domains == set(),
    set(),
    selected_domains
)


# note: Display the final regression baseline in the same simple
# format used by the other JARVIS test suites.
total = passed + failed

print()
print(
    f"Passed: {passed}"
)
print(
    f"Failed: {failed}"
)
print(
    f"Total:  {total}"
)


# note: Return a failing process status when any regression test
# fails so the suite can later be used in automated checks.
if failed > 0:

    raise SystemExit(
        1
    )
