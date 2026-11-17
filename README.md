# IT Ticket Triage Agent

An LLM-powered service that triages employee IT support tickets. It takes free-text ticket descriptions, then classifies the category and priority, writes a short summary and estimates its confidence. The output is a validated, typed object instead of free-form text.

Built with **Python**, **Microsoft Semantic Kernel** and **Azure OpenAI** (with a plain OpenAI fallback).

## How it works

```
ticket text ──► Semantic Kernel (system prompt + chat history)
            ──► Azure OpenAI / OpenAI chat completion
                (temperature 0.1, response_format = Pydantic schema)
            ──► JSON validated into TicketTriageResult
```

- **Structured outputs:** the Pydantic model `TicketTriageResult` is passed as `response_format`, so the model must return JSON that matches the schema. The response is then validated with `model_validate_json`, and invalid output fails loudly instead of leaking downstream.
- **Provider switch:** if `AZURE_OPENAI_API_KEY` is set, the service uses Azure OpenAI; otherwise it falls back to OpenAI. No code changes needed.
- **Low temperature (0.1)** keeps classifications consistent between runs.

### Output schema

| Field | Type | Values |
|---|---|---|
| `category` | enum | Hardware, Software, Network, Access & Security, Other |
| `priority` | enum | Low, Medium, High, Critical |
| `summary` | string | short description of the issue |
| `confidence_score` | float | 0.0 – 1.0 |

Example output (illustrative):

```json
{
  "category": "Network",
  "priority": "High",
  "summary": "Office Wi-Fi drops every few minutes in the 2nd-floor conference room, affecting multiple users.",
  "confidence_score": 0.9
}
```

## Tests and evaluation

`tests/` contains two kinds of tests. Both call the real model, so they need valid API credentials.

- **Contract test:** checks that the response always matches the schema (enum types, confidence range, non-empty summary).
- **Behavioral evals:** a small labelled dataset (`tests/test_data.py`) of realistic tickets: boot failure after an update, Teams audio, Wi-Fi drops and VPN lockout. Each case asserts the expected category and a **minimum** priority, so the agent may escalate but never under-prioritize.

```bash
pytest -v
```

## Setup

Requires Python 3.12+.

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # then fill in your keys
```

`.env`: set the Azure OpenAI variables **or** the OpenAI ones:

```
AZURE_OPENAI_DEPLOYMENT_NAME=...
AZURE_OPENAI_ENDPOINT=...
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_API_VERSION=2024-12-01-preview

OPENAI_MODEL_ID=...
OPENAI_API_KEY=...
```

Run the demo ticket:

```bash
python -m src.service
```

## Project structure

```
src/
  schemas.py   # Pydantic models and enums (TicketTriageResult)
  service.py   # TicketTriageService: Semantic Kernel setup + analyze_ticket()
tests/
  test_data.py    # labelled evaluation dataset
  test_triage.py  # schema contract test + behavioral evals
```

## Possible next steps

- Expose the service as a REST endpoint (FastAPI) for helpdesk integration
- Route tickets to the matching support queue based on category
- Extend the evaluation set and track accuracy across prompt or model changes
