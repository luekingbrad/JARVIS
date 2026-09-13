import ollama


# note: Normalize user requests before deterministic routing checks.
def normalize_request(question):
    return " ".join(
        question.lower().strip().split()
    )


# note: Route clear conversational, explanation, and factual
# requests deterministically before asking the model.
def select_deterministic_skill(question):
    normalized = normalize_request(
        question
    )

    # note: Recognize simple conversational requests that do not
    # require factual knowledge or explanation.
    conversation_phrases = {
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
        "how are you?",
        "how are you"
    }

    if normalized in conversation_phrases:
        return "conversation"

    # note: Explicit teaching or explanation language should always
    # route through the knowledge-grounded explanation skill.
    explanation_phrases = (
        "explain ",
        "explain to me ",
        "help me understand ",
        "break down ",
        "breakdown ",
        "teach me ",
        "simplify ",
        "walk me through "
    )

    if normalized.startswith(
        explanation_phrases
    ):
        return "explain"

    # note: Clear factual question forms should route through the
    # knowledge-grounded question-answering skill.
    factual_phrases = (
        "what is ",
        "what are ",
        "what does ",
        "what do ",
        "which ",
        "who is ",
        "who are ",
        "when is ",
        "when are ",
        "where is ",
        "where are "
    )

    if normalized.startswith(
        factual_phrases
    ):
        return "answer_question"

    return None


def select_skill(question, skills):
    """Select the most appropriate skill for a user request."""

    # note: Use deterministic routing first for requests whose intent
    # is clear enough that model interpretation is unnecessary.
    deterministic_skill = select_deterministic_skill(
        question
    )

    if (
        deterministic_skill is not None
        and deterministic_skill in skills
    ):
        return deterministic_skill

    # note: Build a readable list of available skills so the
    # routing model can choose only from skills JARVIS actually has.
    skill_descriptions = ""

    for skill_name, skill_content in skills.items():
        skill_descriptions += f"""

SKILL: {skill_name}

{skill_content}

--------------------

"""

    # note: Use the local model only when deterministic routing
    # cannot confidently classify the user's intent.
    prompt = f"""

You are the routing component of JARVIS.

Your ONLY task is to classify the user's request into one of the
available skills.

AVAILABLE SKILLS:

{skill_descriptions}

ROUTING RULES:

Choose "conversation" when the user wants:

- a greeting
- a conversational acknowledgment
- casual interaction
- a thank-you response
- a simple conversational reply
- normal conversation that does not require factual knowledge

Choose "explain" when the user wants:

- an explanation
- a concept broken down
- something taught
- something simplified
- help understanding a concept
- an explanation for a beginner

Choose "answer_question" when the user wants:

- a factual answer
- a specific piece of information
- a definition
- a list
- specific responsibilities
- specific facts from the knowledge base

IMPORTANT:

If the user is only greeting JARVIS, acknowledging something,
thanking JARVIS, or otherwise making normal conversation,
choose "conversation".

If the user explicitly asks to explain, teach, simplify,
break down, or help them understand something,
choose "explain".

If the user asks for specific factual information without
requesting an explanation, choose "answer_question".

Do not classify factual knowledge requests as "conversation".

Do not classify explanation requests as "conversation".

USER REQUEST:

{question}

Return ONLY ONE of these exact values:

conversation
explain
answer_question

Do not provide an explanation.

Do not answer the user's question.

Do not include punctuation.

Do not include quotation marks.

Do not include any other text.

"""

    response = ollama.chat(
        model="llama3.1:8b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    selected_skill = response["message"]["content"].strip()

    # note: Fail closed to the knowledge-grounded question skill if
    # the model returns a value that is not an available JARVIS skill.
    if selected_skill not in skills:
        return "answer_question"

    return selected_skill
