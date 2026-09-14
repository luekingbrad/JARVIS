# note: Import the JARVIS tool-registration system so
# temporary permission-test tools can be registered.
from tools.registry import register_tool


# note: Define a harmless test tool representing an action
# that would normally require explicit user confirmation.
def test_confirmed_action():

    """Return a harmless confirmation test result."""

    return (
        "Confirmation-required test tool executed successfully."
    )


# note: Define a harmless test tool representing an action
# that JARVIS should never be allowed to execute.
def test_blocked_action():

    """Return a harmless blocked-tool test result."""

    return (
        "Blocked test tool executed. "
        "This message should never appear."
    )


# note: Register the confirmation-required test tool while
# preventing the language model from ever proposing it.
register_tool(
    name="test_confirmed_action",
    description=(
        "A harmless temporary tool used to verify that "
        "confirmation-required permissions are enforced."
    ),
    permission_level="confirm_required",
    function=test_confirmed_action,
    model_selectable=False
)


# note: Register the blocked test tool while preventing
# the language model from ever proposing it.
register_tool(
    name="test_blocked_action",
    description=(
        "A harmless temporary tool used to verify that "
        "blocked permissions are enforced."
    ),
    permission_level="blocked",
    function=test_blocked_action,
    model_selectable=False
)
