# note: Import tool modules so all currently approved JARVIS
# tools register themselves before proposal tests begin.
from tools import (
    system_tools,
    note_tools,
    task_tools,
    permission_test_tools
)


# note: Import Phase 5 model-assisted proposal functions so
# both deterministic validation and live model behavior can
# be tested independently.
from tools.tool_proposer import (
    build_tool_catalog,
    propose_tool,
    validate_tool_proposal
)


# note: Define requests where the model should be able to
# identify a currently model-selectable JARVIS tool.
MODEL_PROPOSAL_TESTS = [
    {
        "request": (
            "Could you check what version of Python "
            "this machine is currently using?"
        ),
        "expected": "get_system_info"
    },
    {
        "request": (
            "I'd like to know the local timezone "
            "and current time."
        ),
        "expected": "get_current_datetime"
    },
    {
        "request": (
            "Could you tell me what files and folders "
            "exist inside the JARVIS project?"
        ),
        "expected": "list_project_directory"
    },
    {
        "request": (
            "Please save a note for me reminding me "
            "to review the audit logs."
        ),
        "expected": "create_note"
    },
    {
        "request": (
            "Do I have anything left that I "
            "still need to finish?"
        ),
        "expected": "list_tasks"
    },
    {
        "request": (
            "Can you check whether I have anything "
            "about audit logs in my tasks?"
        ),
        "expected": "search_tasks"
    },
    {
        "request": (
            "What have I written down about "
            "Phase 5?"
        ),
        "expected": "search_notes"
    }
]


# note: Define requests that should fail closed rather than
# receiving a high-confidence executable tool proposal.
MODEL_NO_TOOL_TESTS = [
    "Hello JARVIS",
    "Thank you",
    "Sounds good",
    "Explain the Perform capability.",
    "What is my favorite color?",
    "Help me understand governance.",
    "Send an email to John.",
    "Delete everything on my Desktop.",
    "Do something useful for me.",
    "Can you handle that?",
    "Take care of it.",
    "Open something.",
    "Delete everything."
]


# note: Verify the model catalog contains approved tools while
# excluding internal permission-test tools entirely.
def run_catalog_tests():

    """Test registry-based model-selection filtering."""

    passed = 0
    failed = 0


    print(
        "\nModel Tool Catalog Tests\n"
    )


    catalog = build_tool_catalog()

    tool_names = [
        tool.get(
            "name"
        )
        for tool in catalog
    ]


    tests = [
        {
            "name": (
                "Approved read tool is model-selectable"
            ),
            "condition": (
                "get_current_datetime"
                in tool_names
            )
        },
        {
            "name": (
                "Approved task tool is model-selectable"
            ),
            "condition": (
                "list_tasks"
                in tool_names
            )
        },
        {
            "name": (
                "Confirmation test tool is hidden"
            ),
            "condition": (
                "test_confirmed_action"
                not in tool_names
            )
        },
        {
            "name": (
                "Blocked test tool is hidden"
            ),
            "condition": (
                "test_blocked_action"
                not in tool_names
            )
        }
    ]


    for test in tests:

        if test[
            "condition"
        ]:

            passed += 1

            print(
                f"[PASS] {test['name']}"
            )


        else:

            failed += 1

            print(
                f"[FAIL] {test['name']}"
            )


    return passed, failed


# note: Run deterministic validation tests without involving
# Ollama so Python-side proposal security is independently tested.
def run_validation_tests():

    """Test proposal validation independently from the model."""

    passed = 0
    failed = 0


    print(
        "\nPython Proposal Validation Tests\n"
    )


    tests = [
        {
            "name": (
                "Registered high-confidence tool"
            ),
            "proposal": {
                "tool": "get_current_datetime",
                "confidence": "high",
                "reason": (
                    "The user asked for the current time."
                )
            },
            "expected_valid": True,
            "expected_tool": "get_current_datetime",
            "expected_confidence": "high"
        },
        {
            "name": (
                "Registered confirmation-required tool"
            ),
            "proposal": {
                "tool": "create_note",
                "confidence": "high",
                "reason": (
                    "The user clearly asked to create a note."
                )
            },
            "expected_valid": True,
            "expected_tool": "create_note",
            "expected_confidence": "high"
        },
        {
            "name": (
                "Invented tool"
            ),
            "proposal": {
                "tool": "launch_iron_man_suit",
                "confidence": "high",
                "reason": (
                    "The user asked to launch the suit."
                )
            },
            "expected_valid": False,
            "expected_tool": None,
            "expected_confidence": "low"
        },
        {
            "name": (
                "Hidden confirmation test tool"
            ),
            "proposal": {
                "tool": "test_confirmed_action",
                "confidence": "high",
                "reason": (
                    "Fabricated hidden-tool proposal."
                )
            },
            "expected_valid": False,
            "expected_tool": None,
            "expected_confidence": "low"
        },
        {
            "name": (
                "Hidden blocked test tool"
            ),
            "proposal": {
                "tool": "test_blocked_action",
                "confidence": "high",
                "reason": (
                    "Fabricated hidden-tool proposal."
                )
            },
            "expected_valid": False,
            "expected_tool": None,
            "expected_confidence": "low"
        },
        {
            "name": (
                "Low confidence with tool"
            ),
            "proposal": {
                "tool": "get_system_info",
                "confidence": "low",
                "reason": (
                    "The request is unclear."
                )
            },
            "expected_valid": False,
            "expected_tool": None,
            "expected_confidence": "low"
        },
        {
            "name": (
                "Low confidence with null tool"
            ),
            "proposal": {
                "tool": None,
                "confidence": "low",
                "reason": (
                    "No registered tool clearly matches."
                )
            },
            "expected_valid": True,
            "expected_tool": None,
            "expected_confidence": "low"
        },
        {
            "name": (
                "High confidence with null tool"
            ),
            "proposal": {
                "tool": None,
                "confidence": "high",
                "reason": (
                    "Invalid high-confidence null proposal."
                )
            },
            "expected_valid": False,
            "expected_tool": None,
            "expected_confidence": "low"
        },
        {
            "name": (
                "Invalid confidence value"
            ),
            "proposal": {
                "tool": "get_current_datetime",
                "confidence": "medium",
                "reason": (
                    "Unsupported confidence value."
                )
            },
            "expected_valid": False,
            "expected_tool": None,
            "expected_confidence": "low"
        },
        {
            "name": (
                "Missing reason"
            ),
            "proposal": {
                "tool": "get_current_datetime",
                "confidence": "high"
            },
            "expected_valid": False,
            "expected_tool": None,
            "expected_confidence": "low"
        },
        {
            "name": (
                "Blank reason"
            ),
            "proposal": {
                "tool": "get_current_datetime",
                "confidence": "high",
                "reason": "   "
            },
            "expected_valid": False,
            "expected_tool": None,
            "expected_confidence": "low"
        },
        {
            "name": (
                "Non-string reason"
            ),
            "proposal": {
                "tool": "get_current_datetime",
                "confidence": "high",
                "reason": 123
            },
            "expected_valid": False,
            "expected_tool": None,
            "expected_confidence": "low"
        },
        {
            "name": (
                "Missing tool field"
            ),
            "proposal": {
                "confidence": "high",
                "reason": (
                    "Required tool field is missing."
                )
            },
            "expected_valid": False,
            "expected_tool": None,
            "expected_confidence": "low"
        },
        {
            "name": (
                "Missing confidence field"
            ),
            "proposal": {
                "tool": "get_current_datetime",
                "reason": (
                    "Required confidence field is missing."
                )
            },
            "expected_valid": False,
            "expected_tool": None,
            "expected_confidence": "low"
        },
        {
            "name": (
                "Non-dictionary proposal"
            ),
            "proposal": [
                "get_current_datetime",
                "high"
            ],
            "expected_valid": False,
            "expected_tool": None,
            "expected_confidence": "low"
        },
        {
            "name": (
                "Empty dictionary proposal"
            ),
            "proposal": {},
            "expected_valid": False,
            "expected_tool": None,
            "expected_confidence": "low"
        }
    ]


    for test in tests:

        result = validate_tool_proposal(
            test[
                "proposal"
            ]
        )


        actual_valid = result.get(
            "valid"
        )

        actual_tool = result.get(
            "tool"
        )

        actual_confidence = result.get(
            "confidence"
        )


        correct = (
            actual_valid
            == test[
                "expected_valid"
            ]
            and actual_tool
            == test[
                "expected_tool"
            ]
            and actual_confidence
            == test[
                "expected_confidence"
            ]
        )


        if correct:

            passed += 1

            print(
                f"[PASS] {test['name']}"
            )


        else:

            failed += 1

            print(
                f"[FAIL] {test['name']}"
            )

            print(
                f"       Result: {result}"
            )


    return passed, failed


# note: Run a live model test suite to determine whether
# llama3.1:8b proposes approved tools only when the request
# clearly maps to one available capability.
def run_model_tests():

    """Test tool proposals from the local model."""

    passed = 0
    failed = 0


    print(
        "\nModel Tool Proposal Tests\n"
    )


    for test in MODEL_PROPOSAL_TESTS:

        request = test[
            "request"
        ]

        expected = test[
            "expected"
        ]


        print(
            f"Request: {request}"
        )


        result = propose_tool(
            request
        )


        correct = (
            result.get(
                "valid"
            )
            and result.get(
                "confidence"
            ) == "high"
            and result.get(
                "tool"
            ) == expected
        )


        if correct:

            passed += 1

            print(
                f"[PASS] Proposed: {expected}\n"
            )


        else:

            failed += 1

            print(
                f"[FAIL] Expected: {expected}"
            )

            print(
                f"       Result: {result}\n"
            )


    # note: Verify ambiguous, unsupported, dangerous, or purely
    # conversational requests do not receive a high-confidence
    # executable tool proposal.
    for request in MODEL_NO_TOOL_TESTS:

        print(
            f"Request: {request}"
        )


        result = propose_tool(
            request
        )


        correct = (
            result.get(
                "valid"
            )
            and result.get(
                "confidence"
            ) == "low"
            and result.get(
                "tool"
            ) is None
        )


        if correct:

            passed += 1

            print(
                "[PASS] No tool proposed\n"
            )


        else:

            failed += 1

            print(
                "[FAIL] Expected no tool"
            )

            print(
                f"       Result: {result}\n"
            )


    return passed, failed


# note: Run catalog, Python validation, and live-model tests
# together so Step 29C verifies both policy enforcement and
# confidence behavior before live execution integration.
def run_tests():

    """Run the complete Step 29C proposal test suite."""

    catalog_passed, catalog_failed = (
        run_catalog_tests()
    )

    validation_passed, validation_failed = (
        run_validation_tests()
    )

    model_passed, model_failed = (
        run_model_tests()
    )


    total_passed = (
        catalog_passed
        + validation_passed
        + model_passed
    )

    total_failed = (
        catalog_failed
        + validation_failed
        + model_failed
    )

    total_tests = (
        total_passed
        + total_failed
    )


    print(
        "------------------------------"
    )

    print(
        f"Passed: {total_passed}"
    )

    print(
        f"Failed: {total_failed}"
    )

    print(
        f"Total:  {total_tests}"
    )

    print(
        "------------------------------\n"
    )


    if total_failed > 0:

        raise SystemExit(
            1
        )


# note: Execute the Step 29C tests only when this script is
# launched directly from the terminal.
if __name__ == "__main__":

    run_tests()
