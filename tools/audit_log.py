# note: Import Python tools used to create structured
# append-only audit records for JARVIS actions.
from datetime import datetime
from pathlib import Path
import json


# note: Define the local file where JARVIS action records
# will be stored as JSON Lines.
AUDIT_LOG_FILE = Path(
    "logs/actions.jsonl"
)


# note: Define the action statuses recognized by
# JARVIS's Phase 4 audit system.
VALID_ACTION_STATUSES = {
    "requested",
    "confirmation_required",
    "confirmed",
    "canceled",
    "blocked",
    "executed",
    "failed",
    "denied"
}


# note: Remove sensitive or unnecessary information from
# tool arguments before they are written to the audit log.
def sanitize_arguments(
    tool_name,
    arguments
):

    """Return safe metadata describing tool arguments."""

    if not arguments:

        return {}


    # note: Do not duplicate note contents inside the audit log.
    # Record only that note content was supplied.
    if tool_name == "create_note":

        content = arguments.get(
            "content"
        )


        if isinstance(
            content,
            str
        ):

            return {
                "content_supplied": True,
                "content_length": len(
                    content
                )
            }


        return {
            "content_supplied": False
        }


    # note: Fail conservatively for future tools by recording
    # argument names rather than their actual values.
    return {
        "argument_names": sorted(
            arguments.keys()
        )
    }


# note: Create one append-only audit record describing
# an attempted or completed JARVIS action.
def log_action(
    tool_name,
    permission_level,
    status,
    arguments=None,
    details=None
):

    """Append one action record to the JARVIS audit log."""

    # note: Reject unknown statuses so the audit trail
    # remains predictable and consistent.
    if status not in VALID_ACTION_STATUSES:

        raise ValueError(
            f"Invalid action status: {status}"
        )


    # note: Ensure the audit-log directory exists before
    # attempting to append a record.
    AUDIT_LOG_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )


    # note: Generate an offset-aware local timestamp so each
    # action record includes useful chronological information.
    timestamp = datetime.now().astimezone().isoformat(
        timespec="seconds"
    )


    safe_arguments = sanitize_arguments(
        tool_name,
        arguments or {}
    )


    record = {
        "timestamp": timestamp,
        "tool": tool_name,
        "permission_level": permission_level,
        "status": status,
        "arguments": safe_arguments
    }


    # note: Add optional non-sensitive result metadata when
    # useful information is available.
    if details:

        record[
            "details"
        ] = details


    # note: Append one complete JSON object followed by a newline
    # so existing audit history is never rewritten.
    with open(
        AUDIT_LOG_FILE,
        "a",
        encoding="utf-8"
    ) as log_file:

        log_file.write(
            json.dumps(
                record,
                ensure_ascii=False
            ) + "\n"
        )


    return record
