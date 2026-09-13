# JARVIS

JARVIS is a local personal AI assistant built in Python with Ollama.

The project is designed around a core principle:

> The language model may interpret or recommend an action, but Python 
decides what JARVIS is actually allowed to do.

JARVIS combines local language-model inference with controlled tools, 
persistent memory, structured knowledge retrieval, permission handling, 
audit logging, and regression testing.

The current version represents the completion of **Phase 6: Knowledge 
Intelligence**.

## Current Status

* Local AI assistant
* Ollama-powered language model
* Persistent conversational memory
* Skill routing
* Structured local knowledge retrieval
* Knowledge chunking and metadata
* Knowledge-domain isolation
* Source-aware answers
* Fail-closed knowledge behavior
* Controlled tool execution
* Tool permission levels
* User confirmation for state-changing actions
* Notes and task management
* Audit logging
* Automated regression testing

Current regression baseline:

```text
442 passed
0 failed
```

## Architecture

JARVIS separates language-model reasoning from execution authority.

```text
User Request
     |
     v
Skill / Tool Routing
     |
     +----------------------+
     |                      |
     v                      v
Knowledge Path          Tool Path
     |                      |
     v                      v
Domain Selection        Tool Selection
     |                      |
     v                      v
Knowledge Retrieval     Argument Preparation
     |                      |
     v                      v
Evidence Validation     Permission Validation
     |                      |
     v                      v
JARVIS Brain            Confirmation if Required
     |                      |
     v                      v
Grounded Response       Python Execution
                            |
                            v
                       Audit Logging
```

The language model does not receive direct execution authority.

Python controls:

* registered tools;
* tool arguments;
* permission levels;
* confirmation requirements;
* action validation;
* execution;
* audit logging.

## Safety Model

JARVIS follows several core safety principles.

### Python Controls Actions

The model may select or recommend a tool, but Python determines whether 
that tool can execute.

### State-Changing Actions Require Permission

Actions such as creating, editing, completing, or deleting user data can 
require confirmation before execution.

### No False Action Claims

If Python does not return a successful tool result, JARVIS should not 
claim that an action occurred.

### Knowledge Fails Closed

For knowledge-grounded requests, JARVIS uses its approved local knowledge 
base.

If sufficient knowledge is unavailable, JARVIS responds that it does not 
have enough information rather than silently substituting outside model 
knowledge.

### Domain Isolation

Knowledge can be organized into domains such as:

```text
grcp
nist
coursework
risk_management
```

If a user explicitly requests a domain that is not available, retrieval 
fails closed rather than using information from another domain.

## Knowledge Architecture

Knowledge is organized using a domain-based structure.

Example:

```text
knowledge/
├── grcp/
│   ├── capability_model.md
│   ├── learn.md
│   ├── align.md
│   ├── perform.md
│   └── review.md
│
└── nist/
    └── sp_800_160/
        ├── overview.md
        ├── cyber_resiliency.md
        └── design_principles.md
```

The public repository does not include the developer's private knowledge 
files.

The `knowledge/` directory is intentionally preserved as an empty local 
knowledge location.

## Knowledge Retrieval

JARVIS does not rely only on whole-document matching.

Markdown documents are divided into structured sections containing 
metadata such as:

```text
filename
document_title
heading
heading_level
section_path
domain
source_group
chunk_id
content
```

Retrieval considers:

* content matches;
* heading matches;
* filename matches;
* heading intent;
* evidence thresholds;
* source diversity;
* allowed knowledge domains.

This allows JARVIS to retrieve the relevant section of a document rather 
than passing an entire knowledge base to the model.

## Skills

JARVIS currently includes three primary skills.

### Conversation

Handles ordinary conversational requests such as greetings, 
acknowledgments, and casual interaction.

### Answer Question

Handles factual questions that should be answered from the approved local 
knowledge base.

### Explain

Handles requests to explain or simplify concepts using approved local 
knowledge.

Skill selection uses a hybrid approach:

```text
Clear request
    |
    v
Deterministic Python routing

Ambiguous request
    |
    v
Language-model classification
```

## Tools

Current tool capabilities include:

### System

* retrieve system information;
* retrieve the current local date and time;
* list the JARVIS project directory.

### Notes

* create notes;
* list notes;
* read notes;
* search notes;
* edit notes;
* delete notes.

### Tasks

* create tasks;
* list tasks;
* search tasks;
* filter tasks;
* complete tasks;
* delete tasks.

Tool availability and permissions are controlled through the Python 
registry.

## Permission Levels

Tools can be assigned different permission requirements.

Examples include:

```text
safe_read
confirm_required
```

Read-only actions may execute without confirmation.

State-changing actions can require explicit user approval before Python 
executes them.

## Tool Proposal Safety

JARVIS uses both deterministic tool routing and model-assisted tool 
proposals.

Model proposals are validated against the registered tool catalog before 
they are eligible for execution.

Conversational requests such as:

```text
Hello JARVIS
Thank you
Sounds good
```

are rejected as tool requests before a model proposal can turn them into 
an unrelated action.

## Persistent Memory

JARVIS supports local persistent memory.

Runtime memory files are intentionally excluded from the public 
repository.

```text
memory/
```

This prevents personal conversational information from being committed to 
GitHub.

## Notes and Tasks

JARVIS stores notes and tasks locally.

```text
notes/
tasks/
```

The actual user-generated contents of these directories are excluded from 
version control.

The repository preserves only the directory structure.

## Audit Logging

JARVIS records tool activity through its audit logging system.

Runtime audit data is stored under:

```text
logs/
```

Audit logs are excluded from the public repository to prevent local 
activity from being exposed.

## Project Structure

```text
JARVIS/
├── agent.py
├── brain.py
├── memory.py
├── router.py
├── knowledge_importer.py
├── knowledge_retriever.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── config/
│   └── system.md
│
├── skills/
│   ├── answer_question.md
│   ├── conversation.md
│   └── explain.md
│
├── tools/
│   ├── __init__.py
│   ├── action_validator.py
│   ├── audit_log.py
│   ├── note_tools.py
│   ├── permission_test_tools.py
│   ├── registry.py
│   ├── system_tools.py
│   ├── task_tools.py
│   ├── tool_arguments.py
│   ├── tool_proposer.py
│   └── tool_router.py
│
├── knowledge/
├── memory/
├── notes/
├── tasks/
├── logs/
│
├── tests_tool_arguments.py
├── tests_tool_router.py
├── tests_tool_proposer.py
├── tests_router.py
├── tests_knowledge_retriever.py
└── tests_knowledge_importer.py
```

## Requirements

JARVIS has been tested with:

```text
Python 3.14.0
Ollama
llama3.1:8b
```

Python dependencies are listed in:

```text
requirements.txt
```

Install them with:

```bash
pip install -r requirements.txt
```

## Ollama Setup

JARVIS uses Ollama for local language-model inference.

Install Ollama separately for your operating system.

After Ollama is installed, pull the model used by the current JARVIS 
configuration:

```bash
ollama pull llama3.1:8b
```

Verify that Ollama can see the model:

```bash
ollama list
```

## Local Setup

Clone the repository:

```bash
git clone <repository-url>
cd JARVIS
```

Create a Python virtual environment:

```bash
python -m venv .venv
```

Activate it on macOS or Linux:

```bash
source .venv/bin/activate
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Ensure Ollama is installed and the configured model is available.

Then start JARVIS:

```bash
python agent.py
```

## Adding Knowledge

Private knowledge files can be added locally under:

```text
knowledge/
```

Recommended structure:

```text
knowledge/
└── domain/
    └── optional_source_group/
        └── topic.md
```

For example:

```text
knowledge/
└── nist/
    └── sp_800_160/
        └── cyber_resiliency.md
```

The knowledge importer also supports structured importing of Markdown and 
text files.

Because `knowledge/` is ignored by Git by default, local knowledge does 
not automatically become part of the public repository.

## Testing

Run the regression suites with:

```bash
python tests_tool_arguments.py
python tests_tool_router.py
python tests_tool_proposer.py
python tests_router.py
python tests_knowledge_retriever.py
python tests_knowledge_importer.py
```

Current baseline:

```text
Tool arguments:       194 / 194
Tool router:          102 / 102
Tool proposer:         40 / 40
Skill router:          11 / 11
Knowledge retriever:   82 / 82
Knowledge importer:    13 / 13

Total:                442 / 442
```

## Privacy

The repository is configured to exclude local user data.

The following are ignored by Git:

```text
.venv/
__pycache__/
logs/*
memory/*
notes/*
tasks/*
knowledge/*
.env
.env.*
*.pem
*.key
```

This keeps local memory, notes, tasks, audit logs, knowledge documents, 
environment files, and common secret files outside the public repository.

Always review:

```bash
git status
```

before committing changes.

## Development Progress

JARVIS has been developed in phases.

### Phase 1

Core JARVIS Foundation

### Phase 2

Skills and Local Knowledge

### Phase 3

Persistent Memory and Controlled Conversational Context

### Phase 4

Tools, Actions, Permission Control, and Audit Logging

### Phase 5

Assistant Capabilities, Tool Selection, and Action Safety

### Phase 6

Knowledge Intelligence, Source Awareness, Domain Control, and Grounded 
Reasoning

## Project Philosophy

JARVIS is being developed as a personal AI agent rather than as an 
unrestricted autonomous system.

The project prioritizes:

* local execution;
* user control;
* explicit permissions;
* deterministic safety boundaries;
* knowledge provenance;
* fail-closed behavior;
* regression testing;
* incremental capability development.

The goal is not simply to make JARVIS more autonomous.

The goal is to make JARVIS more capable **without giving up control, 
transparency, or reliability**.

