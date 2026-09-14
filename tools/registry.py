# note: Store the tools that JARVIS is allowed to discover
# and potentially execute.
TOOL_REGISTRY = {}


# note: Define the permission levels recognized by
# JARVIS's Phase 4 tool-security system.
VALID_PERMISSION_LEVELS = {
    "safe_read",
    "confirm_required",
    "blocked"
}


# note: Register a tool with JARVIS using consistent security
# metadata, including whether the language model may propose it.
def register_tool(
    name,
    description,
    permission_level,
    function,
    model_selectable=True
):

    """Register a tool that JARVIS can use."""

    # note: Reject tools using unknown permission levels so
    # every registered tool has an explicit security policy.
    if permission_level not in VALID_PERMISSION_LEVELS:

        raise ValueError(
            f"Invalid permission level: {permission_level}"
        )


    # note: Require model-selection eligibility to be an explicit
    # boolean so malformed registry metadata fails during startup.
    if not isinstance(
        model_selectable,
        bool
    ):

        raise ValueError(
            "model_selectable must be True or False."
        )


    TOOL_REGISTRY[name] = {
        "name": name,
        "description": description,
        "permission_level": permission_level,
        "model_selectable": model_selectable,
        "function": function
    }


# note: Return every tool currently registered with JARVIS.
def get_registered_tools():

    """Return all registered JARVIS tools."""

    return TOOL_REGISTRY


# note: Return one registered tool by its unique name.
def get_tool(name):

    """Return a specific registered tool."""

    return TOOL_REGISTRY.get(
        name
    )


# note: Determine whether a registered tool is eligible for
# model-assisted selection without granting execution authority.
def is_tool_model_selectable(
    name
):

    """Return True only when the model may propose the tool."""

    tool = get_tool(
        name
    )


    # note: Unregistered tools are never eligible for model
    # selection, regardless of any model-generated proposal.
    if not tool:

        return False


    return tool.get(
        "model_selectable",
        False
    ) is True


# note: Check whether a tool is allowed to execute based on
# its permission level and the user's confirmation state.
def check_tool_permission(
    tool,
    confirmed=False
):

    """Determine whether a registered tool may execute."""

    permission_level = tool.get(
        "permission_level"
    )


    # note: Safe read-only tools may execute immediately
    # without asking the user for confirmation.
    if permission_level == "safe_read":

        return {
            "allowed": True,
            "requires_confirmation": False,
            "reason": None
        }


    # note: Confirmation-required tools may execute only
    # after explicit user confirmation has been supplied.
    if permission_level == "confirm_required":

        if confirmed:

            return {
                "allowed": True,
                "requires_confirmation": False,
                "reason": None
            }


        return {
            "allowed": False,
            "requires_confirmation": True,
            "reason": (
                "This tool requires explicit user confirmation."
            )
        }


    # note: Blocked tools may never execute, even when a
    # confirmation flag is supplied.
    if permission_level == "blocked":

        return {
            "allowed": False,
            "requires_confirmation": False,
            "reason": (
                "This tool is blocked by JARVIS's permission policy."
            )
        }


    # note: Fail closed if a tool somehow contains an
    # unrecognized permission level.
    return {
        "allowed": False,
        "requires_confirmation": False,
        "reason": (
            "The tool has an invalid permission configuration."
        )
    }


# note: Execute a registered tool only after its permission
# policy has been evaluated successfully.
def execute_tool(
    name,
    confirmed=False,
    **kwargs
):

    """Execute a registered JARVIS tool."""

    tool = get_tool(
        name
    )


    # note: Refuse execution when the requested tool
    # does not exist in the registry.
    if not tool:

        return {
            "success": False,
            "executed": False,
            "tool": name,
            "error": "Tool is not registered."
        }


    permission_level = tool.get(
        "permission_level"
    )


    # note: Ask the permission system whether this tool
    # is currently allowed to execute.
    permission_result = check_tool_permission(
        tool,
        confirmed=confirmed
    )


    # note: Return a structured response rather than executing
    # a tool whose permission policy has not been satisfied.
    if not permission_result.get(
        "allowed"
    ):

        return {
            "success": False,
            "executed": False,
            "tool": name,
            "permission_level": permission_level,
            "requires_confirmation": permission_result.get(
                "requires_confirmation",
                False
            ),
            "error": permission_result.get(
                "reason"
            )
        }


    function = tool[
        "function"
    ]


    # note: Catch tool failures so one broken tool does
    # not crash the entire JARVIS application.
    try:

        result = function(
            **kwargs
        )


        return {
            "success": True,
            "executed": True,
            "tool": name,
            "permission_level": permission_level,
            "requires_confirmation": False,
            "result": result
        }


    except Exception as error:

        return {
            "success": False,
            "executed": False,
            "tool": name,
            "permission_level": permission_level,
            "requires_confirmation": False,
            "error": str(
                error
            )
        }
