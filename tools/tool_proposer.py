# note: Import JSON handling so JARVIS can require the model
# to return a small machine-readable tool proposal.
import json


# note: Import Ollama so the local language model can evaluate
# requests the deterministic router could not confidently match.
import ollama


# note: Import the authoritative tool registry so the model
# can only propose tools that Python knows actually exist.
from tools.registry import (
    get_registered_tools,
    get_tool,
    is_tool_model_selectable
)


# note: Define the local model used only for Phase 5
# tool-proposal experiments.
DEFAULT_PROPOSAL_MODEL = "llama3.1:8b"


# note: Build a limited catalog containing only tools that
# are explicitly allowed to participate in model selection.
def build_tool_catalog():

    """Return safe metadata describing model-selectable tools."""

    registered_tools = get_registered_tools()

    catalog = []


    for tool_name, tool in registered_tools.items():

        # note: Completely hide tools that the registry has
        # marked as unavailable for model-assisted selection.
        if not is_tool_model_selectable(
            tool_name
        ):

            continue


        catalog.append(
            {
                "name": tool_name,
                "description": tool.get(
                    "description",
                    ""
                ),
                "permission_level": tool.get(
                    "permission_level",
                    "unknown"
                )
            }
        )


    return catalog


# note: Build a strict prompt that asks the model only to
# propose a tool and never to claim that an action executed.
def build_tool_proposal_prompt(
    request
):

    """Build the model prompt for tool proposal."""

    catalog = build_tool_catalog()


    tool_lines = []


    for tool in catalog:

        tool_lines.append(
            (
                f"- {tool['name']}: "
                f"{tool['description']} "
                f"(permission: "
                f"{tool['permission_level']})"
            )
        )


    tool_catalog_text = "\n".join(
        tool_lines
    )


    return f"""
You are JARVIS's tool-selection assistant.

Your only job is to decide whether the user's request clearly
matches one of the registered tools listed below.

You do NOT execute tools.
You do NOT grant permissions.
You do NOT bypass confirmation requirements.
You do NOT invent tools.
You do NOT answer the user's request.

Registered tools:

{tool_catalog_text}

User request:

{request}

Return ONLY valid JSON using exactly this structure:

{{
  "tool": "registered_tool_name_or_null",
  "confidence": "high_or_low",
  "reason": "brief explanation"
}}

Rules:

1. "tool" must be the exact name of a registered tool shown
   in the tool catalog above, or null.
2. Use confidence "high" only when the request clearly maps
   to one registered tool.
3. Use confidence "low" when the request is ambiguous,
   unrelated, unsupported, or could reasonably mean more
   than one thing.
4. If confidence is "low", tool must be null.
5. Never invent a tool.
6. Never claim an action was executed.
7. Return JSON only.
""".strip()


# note: Extract JSON from the model response while tolerating
# accidental Markdown code fences around otherwise valid JSON.
def extract_json_object(
    response_text
):

    """Extract and parse a JSON object from model output."""

    cleaned = response_text.strip()


    if cleaned.startswith(
        "```"
    ):

        lines = cleaned.splitlines()


        if lines:

            lines = lines[
                1:
            ]


        if lines and lines[
            -1
        ].strip() == "```":

            lines = lines[
                :-1
            ]


        cleaned = "\n".join(
            lines
        ).strip()


    try:

        parsed = json.loads(
            cleaned
        )


    except json.JSONDecodeError:

        return None


    if not isinstance(
        parsed,
        dict
    ):

        return None


    return parsed


# note: Validate every model proposal in Python before any
# future component is allowed to rely on it.
def validate_tool_proposal(
    proposal
):

    """Validate a model-generated tool proposal."""

    if not isinstance(
        proposal,
        dict
    ):

        return {
            "valid": False,
            "tool": None,
            "confidence": "low",
            "error": (
                "Tool proposal must be a dictionary."
            )
        }


    required_fields = {
        "tool",
        "confidence",
        "reason"
    }


    missing_fields = [
        field
        for field in required_fields
        if field not in proposal
    ]


    if missing_fields:

        return {
            "valid": False,
            "tool": None,
            "confidence": "low",
            "error": (
                "Tool proposal is missing required fields: "
                + ", ".join(
                    sorted(
                        missing_fields
                    )
                )
            )
        }


    tool_name = proposal.get(
        "tool"
    )

    confidence = proposal.get(
        "confidence"
    )

    reason = proposal.get(
        "reason"
    )


    # note: Only the two explicitly supported confidence
    # values are accepted from the model.
    if confidence not in {
        "high",
        "low"
    }:

        return {
            "valid": False,
            "tool": None,
            "confidence": "low",
            "error": (
                "Tool proposal contains an invalid "
                "confidence value."
            )
        }


    # note: Require a short textual reason for debugging and
    # future auditability, even though it grants no authority.
    if not isinstance(
        reason,
        str
    ) or not reason.strip():

        return {
            "valid": False,
            "tool": None,
            "confidence": "low",
            "error": (
                "Tool proposal must contain a reason."
            )
        }


    # note: Low-confidence proposals are intentionally forced
    # to contain no executable tool choice.
    if confidence == "low":

        if tool_name is not None:

            return {
                "valid": False,
                "tool": None,
                "confidence": "low",
                "error": (
                    "Low-confidence proposals must use "
                    "a null tool."
                )
            }


        return {
            "valid": True,
            "tool": None,
            "confidence": "low",
            "reason": reason,
            "error": None
        }


    # note: High-confidence proposals must contain a
    # non-empty registered tool name.
    if not isinstance(
        tool_name,
        str
    ) or not tool_name.strip():

        return {
            "valid": False,
            "tool": None,
            "confidence": "low",
            "error": (
                "High-confidence proposals must contain "
                "a registered tool name."
            )
        }


    registered_tool = get_tool(
        tool_name
    )


    # note: Reject hallucinated or misspelled tool names even
    # if the model claims high confidence.
    if not registered_tool:

        return {
            "valid": False,
            "tool": None,
            "confidence": "low",
            "error": (
                f"Proposed tool '{tool_name}' "
                "is not registered."
            )
        }


    # note: Reject registered tools that are explicitly hidden
    # from model-assisted selection by registry policy.
    if not is_tool_model_selectable(
        tool_name
    ):

        return {
            "valid": False,
            "tool": None,
            "confidence": "low",
            "error": (
                f"Proposed tool '{tool_name}' is not "
                "available for model-assisted selection."
            )
        }


    return {
        "valid": True,
        "tool": tool_name,
        "confidence": "high",
        "reason": reason,
        "error": None
    }


# note: Reject simple conversational requests before a model
# proposal can become an executable tool recommendation.
def is_conversational_request(
    request
):

    """Return True when the request is clearly conversational."""

    normalized = " ".join(
        request.lower().strip().split()
    )

    conversational_phrases = {
        "hello",
        "hello jarvis",
        "hi",
        "hi jarvis",
        "hey",
        "hey jarvis",
        "good morning",
        "good afternoon",
        "good evening",
        "thank you",
        "thanks",
        "sounds good",
        "okay",
        "ok",
        "how are you",
        "how are you?"
    }

    return normalized in conversational_phrases


# note: Ask the local model for a tool recommendation and then
# pass the response through deterministic Python validation.
def propose_tool(
    request,
    model=DEFAULT_PROPOSAL_MODEL
):

    """Return a validated model-assisted tool proposal."""

    # note: Fail closed for clearly conversational requests so
    # the model cannot hallucinate an unrelated executable tool.
    if is_conversational_request(
        request
    ):

        return {
            "valid": True,
            "tool": None,
            "confidence": "low",
            "reason": (
                "The request is conversational and does not "
                "require a JARVIS tool."
            ),
            "error": None,
            "raw_response": None
        }


    prompt = build_tool_proposal_prompt(
        request
    )


    try:

        response = ollama.chat(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            options={
                "temperature": 0.1
            }
        )


    except Exception as error:

        return {
            "valid": False,
            "tool": None,
            "confidence": "low",
            "reason": None,
            "error": str(
                error
            )
        }


    response_text = response[
        "message"
    ][
        "content"
    ]


    parsed = extract_json_object(
        response_text
    )


    if parsed is None:

        return {
            "valid": False,
            "tool": None,
            "confidence": "low",
            "reason": None,
            "error": (
                "The model did not return valid JSON."
            ),
            "raw_response": response_text
        }


    validated = validate_tool_proposal(
        parsed
    )


    validated[
        "raw_response"
    ] = response_text


    return validated
