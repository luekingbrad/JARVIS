# note: Import the JARVIS tool registry so action requests
# can be validated against authoritative tool metadata.
from tools.registry import get_tool


# note: Define the fields every JARVIS action request must
# contain before it may continue through the action pipeline.
REQUIRED_ACTION_FIELDS = {
    "tool",
    "arguments",
    "permission_level",
    "request"
}


# note: Validate a structured action request before JARVIS
# allows it to continue to permission evaluation or execution.
def validate_action_request(
    action_request
):

    """Validate a JARVIS action request."""

    # note: Reject anything that is not a dictionary because
    # all JARVIS action requests use a structured mapping.
    if not isinstance(
        action_request,
        dict
    ):

        return {
            "valid": False,
            "error": (
                "Action request must be a dictionary."
            )
        }


    # note: Verify that every required action-request field
    # exists before examining individual values.
    missing_fields = [
        field
        for field in REQUIRED_ACTION_FIELDS
        if field not in action_request
    ]


    if missing_fields:

        return {
            "valid": False,
            "error": (
                "Action request is missing required fields: "
                + ", ".join(
                    sorted(
                        missing_fields
                    )
                )
            )
        }


    tool_name = action_request.get(
        "tool"
    )

    arguments = action_request.get(
        "arguments"
    )

    permission_level = action_request.get(
        "permission_level"
    )

    original_request = action_request.get(
        "request"
    )


    # note: Require a non-empty tool name so malformed or
    # incomplete actions cannot enter the execution pipeline.
    if not isinstance(
        tool_name,
        str
    ) or not tool_name.strip():

        return {
            "valid": False,
            "error": (
                "Action request contains an invalid tool name."
            )
        }


    # note: Verify that the requested tool actually exists
    # in JARVIS's authoritative tool registry.
    registered_tool = get_tool(
        tool_name
    )


    if not registered_tool:

        return {
            "valid": False,
            "error": (
                f"Tool '{tool_name}' is not registered."
            )
        }


    # note: Require tool arguments to use a dictionary so they
    # can be safely expanded into keyword arguments later.
    if not isinstance(
        arguments,
        dict
    ):

        return {
            "valid": False,
            "error": (
                "Action request arguments must be a dictionary."
            )
        }


    # note: Require the original user request to remain attached
    # to the action for traceability and future reasoning.
    if not isinstance(
        original_request,
        str
    ) or not original_request.strip():

        return {
            "valid": False,
            "error": (
                "Action request must contain the original request."
            )
        }


    registered_permission_level = registered_tool.get(
        "permission_level"
    )


    # note: Reject an action if its stored permission metadata
    # does not exactly match the authoritative registry value.
    # This prevents stale or altered action metadata from
    # weakening JARVIS's permission policy.
    if permission_level != registered_permission_level:

        return {
            "valid": False,
            "error": (
                "Action request permission level does not "
                "match the registered tool permission level."
            )
        }


    # note: Return the validated registry metadata so later
    # Phase 5 components can use authoritative tool information.
    return {
        "valid": True,
        "error": None,
        "tool": registered_tool
    }
