from router import select_skill
from agent import load_skills


# note: Load the real JARVIS skill files so these tests verify
# the same routing inputs used by the live agent.
skills = load_skills()


passed = 0
failed = 0


# note: Run one routing test and track the result in a simple
# regression-test format consistent with the rest of JARVIS.
def check(description, request, expected):
    global passed, failed

    actual = select_skill(
        request,
        skills
    )

    if actual == expected:
        passed += 1
        print(
            f"PASS: {description}"
        )
    else:
        failed += 1
        print(
            f"FAIL: {description}"
        )
        print(
            f"  Request:  {request}"
        )
        print(
            f"  Expected: {expected}"
        )
        print(
            f"  Actual:   {actual}"
        )


# note: Verify ordinary conversational requests remain outside
# JARVIS's knowledge-grounded answer and explanation skills.
check(
    "Greeting routes to conversation",
    "Hello JARVIS",
    "conversation"
)

check(
    "Simple greeting routes to conversation",
    "Hi",
    "conversation"
)

check(
    "Thank-you routes to conversation",
    "Thank you",
    "conversation"
)

check(
    "Acknowledgment routes to conversation",
    "Sounds good",
    "conversation"
)

check(
    "General conversational question routes to conversation",
    "How are you?",
    "conversation"
)


# note: Verify explanation requests continue to route through
# JARVIS's knowledge-grounded explanation skill.
check(
    "Explicit explanation routes to explain",
    "Explain governance to me",
    "explain"
)

check(
    "Beginner explanation routes to explain",
    "Help me understand Perform",
    "explain"
)

check(
    "Break-down request routes to explain",
    "Break down the four GRC capabilities for me",
    "explain"
)


# note: Verify factual knowledge requests continue to route
# through JARVIS's knowledge-grounded question-answering skill.
check(
    "Capability question routes to answer_question",
    "What are the four GRC capabilities?",
    "answer_question"
)

check(
    "Definition request routes to answer_question",
    "What is governance?",
    "answer_question"
)

check(
    "Specific responsibility request routes to answer_question",
    "What are the responsibilities of Learn?",
    "answer_question"
)


print(
    f"\nRouter regression results: {passed} passed, {failed} failed"
)


if failed:
    raise SystemExit(
        1
    )
