from pathlib import Path
import argparse
import re


# note: Define the project knowledge directory and the file
# formats accepted by the first version of the importer.
KNOWLEDGE_DIRECTORY = Path(
    "knowledge"
)

SUPPORTED_EXTENSIONS = {
    ".md",
    ".txt"
}


# note: Convert user-provided folder and file names into safe,
# predictable path components for the knowledge directory.
def sanitize_name(
    value
):

    value = value.strip().lower()

    value = re.sub(
        r"[^a-z0-9_-]+",
        "_",
        value
    )

    value = value.strip(
        "_"
    )

    if not value:
        raise ValueError(
            "Knowledge names cannot be empty."
        )

    return value


# note: Validate that the source exists and uses a format the
# current knowledge importer knows how to handle safely.
def validate_source(
    source_path
):

    if not source_path.exists():
        raise FileNotFoundError(
            f"Source file does not exist: {source_path}"
        )

    if not source_path.is_file():
        raise ValueError(
            f"Source path is not a file: {source_path}"
        )

    if (
        source_path.suffix.lower()
        not in SUPPORTED_EXTENSIONS
    ):
        raise ValueError(
            "Unsupported knowledge file type: "
            f"{source_path.suffix}"
        )


# note: Build the destination path using JARVIS's domain and
# optional source-group knowledge organization convention.
def build_destination(
    source_path,
    domain,
    source_group=None,
    topic=None
):

    safe_domain = sanitize_name(
        domain
    )

    destination_directory = (
        KNOWLEDGE_DIRECTORY
        / safe_domain
    )

    if source_group:
        safe_source_group = sanitize_name(
            source_group
        )

        destination_directory = (
            destination_directory
            / safe_source_group
        )

    if topic:
        safe_topic = sanitize_name(
            topic
        )

    else:
        safe_topic = sanitize_name(
            source_path.stem
        )

    destination_path = (
        destination_directory
        / f"{safe_topic}.md"
    )

    return destination_path


# note: Read supported source material without changing its
# wording so imported knowledge remains faithful to the source.
def read_source(
    source_path
):

    return source_path.read_text(
        encoding="utf-8"
    )


# note: Import one knowledge file while refusing to silently
# overwrite material that already exists in JARVIS.
def import_knowledge(
    source_path,
    domain,
    source_group=None,
    topic=None
):

    source_path = Path(
        source_path
    )

    validate_source(
        source_path
    )

    destination_path = build_destination(
        source_path,
        domain,
        source_group,
        topic
    )

    if destination_path.exists():
        raise FileExistsError(
            "Knowledge file already exists: "
            f"{destination_path}"
        )

    destination_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    content = read_source(
        source_path
    )

    destination_path.write_text(
        content,
        encoding="utf-8"
    )

    return destination_path


# note: Provide a simple command-line interface for importing
# new local knowledge without editing JARVIS source code.
def main():

    parser = argparse.ArgumentParser(
        description=(
            "Import Markdown or text knowledge "
            "into JARVIS."
        )
    )

    parser.add_argument(
        "source",
        help="Path to the source .md or .txt file."
    )

    parser.add_argument(
        "domain",
        help=(
            "Top-level knowledge domain, "
            "such as cybersecurity or coursework."
        )
    )

    parser.add_argument(
        "--source-group",
        help=(
            "Optional second-level group, "
            "such as core_400 or sp_800_160."
        )
    )

    parser.add_argument(
        "--topic",
        help=(
            "Optional destination topic filename."
        )
    )

    args = parser.parse_args()

    try:
        destination = import_knowledge(
            args.source,
            args.domain,
            args.source_group,
            args.topic
        )

    except (
        FileNotFoundError,
        FileExistsError,
        ValueError,
        UnicodeDecodeError
    ) as error:
        print(
            f"Import failed: {error}"
        )

        raise SystemExit(
            1
        )

    print(
        "Knowledge imported successfully:"
    )

    print(
        destination
    )


# note: Run the importer only when this file is executed
# directly from the command line.
if __name__ == "__main__":
    main()
