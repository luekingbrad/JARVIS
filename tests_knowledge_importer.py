from pathlib import Path
import tempfile

import knowledge_importer
from knowledge_importer import build_destination
from knowledge_importer import import_knowledge
from knowledge_importer import sanitize_name
from knowledge_importer import validate_source


# note: Track passing and failing importer regression checks
# without requiring an external testing framework.
passed = 0
failed = 0


# note: Record one importer regression-test result and display
# useful information when a check fails.
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
                f"  Actual: {actual}"
            )


# note: Verify user-provided names are converted into safe,
# predictable lowercase path components.
sanitized_name = sanitize_name(
    "Core 400 Systems Thinking"
)

check(
    "Knowledge names are sanitized",
    sanitized_name == "core_400_systems_thinking",
    "core_400_systems_thinking",
    sanitized_name
)


# note: Verify punctuation and surrounding whitespace cannot
# produce unsafe or inconsistent knowledge path names.
sanitized_name = sanitize_name(
    "  NIST SP 800-160!  "
)

check(
    "Knowledge punctuation is sanitized",
    sanitized_name == "nist_sp_800-160",
    "nist_sp_800-160",
    sanitized_name
)


# note: Verify names containing no usable characters fail
# instead of creating an empty knowledge path component.
empty_name_rejected = False

try:
    sanitize_name(
        "!!!"
    )

except ValueError:
    empty_name_rejected = True

check(
    "Empty sanitized knowledge names are rejected",
    empty_name_rejected,
    True,
    empty_name_rejected
)


# note: Use a temporary directory so importer tests never
# modify the user's real JARVIS knowledge base.
with tempfile.TemporaryDirectory() as temporary_directory:

    temporary_path = Path(
        temporary_directory
    )

    original_knowledge_directory = (
        knowledge_importer.KNOWLEDGE_DIRECTORY
    )

    knowledge_importer.KNOWLEDGE_DIRECTORY = (
        temporary_path
        / "knowledge"
    )

    try:

        # note: Create a temporary Markdown source for valid
        # import and destination-path tests.
        markdown_source = (
            temporary_path
            / "systems_thinking.md"
        )

        markdown_source.write_text(
            """
# Systems Thinking

## Purpose

Systems thinking examines relationships across a system.
""".strip(),
            encoding="utf-8"
        )


        # note: Verify valid Markdown source files pass source
        # validation without raising an exception.
        markdown_validation_passed = True

        try:
            validate_source(
                markdown_source
            )

        except Exception:
            markdown_validation_passed = False

        check(
            "Markdown source validation succeeds",
            markdown_validation_passed,
            True,
            markdown_validation_passed
        )


        # note: Verify nested domain and source-group paths are
        # constructed using the agreed knowledge architecture.
        destination = build_destination(
            markdown_source,
            "Coursework",
            "Core 400"
        )

        expected_destination = (
            knowledge_importer.KNOWLEDGE_DIRECTORY
            / "coursework"
            / "core_400"
            / "systems_thinking.md"
        )

        check(
            "Nested knowledge destination is constructed correctly",
            destination == expected_destination,
            expected_destination,
            destination
        )


        # note: Verify an explicitly supplied topic controls the
        # destination filename and is sanitized safely.
        destination = build_destination(
            markdown_source,
            "Cyber Resilience",
            "Design Principles",
            "Resilience Overview"
        )

        expected_destination = (
            knowledge_importer.KNOWLEDGE_DIRECTORY
            / "cyber_resilience"
            / "design_principles"
            / "resilience_overview.md"
        )

        check(
            "Custom topic destination is sanitized",
            destination == expected_destination,
            expected_destination,
            destination
        )


        # note: Verify a real import creates the expected nested
        # Markdown file inside the temporary knowledge directory.
        imported_path = import_knowledge(
            markdown_source,
            "Coursework",
            "Core 400",
            "Systems Thinking"
        )

        expected_imported_path = (
            knowledge_importer.KNOWLEDGE_DIRECTORY
            / "coursework"
            / "core_400"
            / "systems_thinking.md"
        )

        check(
            "Valid knowledge import creates destination file",
            (
                imported_path == expected_imported_path
                and imported_path.exists()
            ),
            expected_imported_path,
            imported_path
        )


        # note: Verify imported material remains textually faithful
        # to the source instead of being silently rewritten.
        source_content = markdown_source.read_text(
            encoding="utf-8"
        )

        imported_content = imported_path.read_text(
            encoding="utf-8"
        )

        check(
            "Imported knowledge preserves source content",
            imported_content == source_content,
            source_content,
            imported_content
        )


        # note: Verify plain-text notes are accepted and converted
        # into a Markdown knowledge destination.
        text_source = (
            temporary_path
            / "risk_notes.txt"
        )

        text_source.write_text(
            "Risk is considered in relation to objectives.",
            encoding="utf-8"
        )

        text_imported_path = import_knowledge(
            text_source,
            "Risk Management"
        )

        expected_text_path = (
            knowledge_importer.KNOWLEDGE_DIRECTORY
            / "risk_management"
            / "risk_notes.md"
        )

        check(
            "Plain-text knowledge imports as Markdown",
            (
                text_imported_path == expected_text_path
                and text_imported_path.exists()
            ),
            expected_text_path,
            text_imported_path
        )


        # note: Verify duplicate destinations are rejected so
        # existing knowledge cannot be silently overwritten.
        duplicate_rejected = False

        try:
            import_knowledge(
                markdown_source,
                "Coursework",
                "Core 400",
                "Systems Thinking"
            )

        except FileExistsError:
            duplicate_rejected = True

        check(
            "Existing knowledge cannot be overwritten",
            duplicate_rejected,
            True,
            duplicate_rejected
        )


        # note: Verify unsupported source formats are rejected
        # before anything is written into the knowledge base.
        unsupported_source = (
            temporary_path
            / "unsupported.pdf"
        )

        unsupported_source.write_text(
            "Test content",
            encoding="utf-8"
        )

        unsupported_rejected = False

        try:
            validate_source(
                unsupported_source
            )

        except ValueError:
            unsupported_rejected = True

        check(
            "Unsupported knowledge formats are rejected",
            unsupported_rejected,
            True,
            unsupported_rejected
        )


        # note: Verify missing source paths fail closed instead
        # of creating empty or misleading knowledge files.
        missing_source = (
            temporary_path
            / "missing.md"
        )

        missing_rejected = False

        try:
            validate_source(
                missing_source
            )

        except FileNotFoundError:
            missing_rejected = True

        check(
            "Missing knowledge source is rejected",
            missing_rejected,
            True,
            missing_rejected
        )


        # note: Verify directories cannot be imported as though
        # they were individual knowledge documents.
        directory_source = (
            temporary_path
            / "source_directory"
        )

        directory_source.mkdir()

        directory_rejected = False

        try:
            validate_source(
                directory_source
            )

        except ValueError:
            directory_rejected = True

        check(
            "Directory source is rejected",
            directory_rejected,
            True,
            directory_rejected
        )

    finally:

        # note: Restore the real knowledge directory after all
        # isolated importer tests finish.
        knowledge_importer.KNOWLEDGE_DIRECTORY = (
            original_knowledge_directory
        )


# note: Display the final importer regression baseline.
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


# note: Return a failing process status when an importer
# regression is detected.
if failed > 0:
    raise SystemExit(
        1
    )
