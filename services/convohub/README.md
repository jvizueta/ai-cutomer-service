# ConvoHub

ConvoHub is a LangGraph-based conversational orchestration hub. It implements a Supervisor ("Orchestrator") architecture where a language model dynamically routes user requests to specialized tool agents.

## Overview
The Orchestrator LLM views agents as tools and decides which one to invoke based on user intent:
- **info-agent**: Answers FAQs with Redis-backed memory and adaptive summarization using an Ollama `llama2.1` model.
- **calendar-scheduler**: Checks availability and schedules meetings on a (stub) Google Calendar.
- **waha-adapter**: Edge microservice receiving WhatsApp webhook events (from WAHA) and handing them to the Orchestrator.

## Architecture
```
          +------------------+
          |   WAHA Service   |
          +---------+--------+
                    |
                (webhook)
                    v
            +---------------+        +-------------------+
            |  waha-adapter | -----> |   Orchestrator    |--(LLM routing)----+
            +---------------+        +-------------------+                   |
                                                       |                     |
                                                       v                     v
                                               +---------------+     +------------------+
                                               |   info-agent  |     | calendar-scheduler|
                                               +---------------+     +------------------+
```

## Components
1. **Orchestrator** (`orchestrator.py`): Uses an LLM (ChatOllama) and a routing prompt to produce either a direct answer or a tool directive of the form `TOOL:<tool_name>:<query>`.
2. **info-agent** (`agents/info_agent.py`): Maintains conversation memory in Redis, applies adaptive summarization, and queries Ollama.
3. **calendar-scheduler** (`agents/calendar_scheduler.py`): A stub for Google Calendar integration performing simple scheduling logic.
4. **WAHA Adapter** (`waha_adapter/main.py`): FastAPI service exposing `/webhook` and `/healthz`.

## Environment Variables
Defined in `.env` / `.env.example`:
- Supervisor: `SUPERVISOR_MODEL`, `SUPERVISOR_TEMPERATURE`, `ORCHESTRATOR_MAX_STEPS`
- Info-Agent: `INFO_AGENT_MODEL`, `INFO_AGENT_SYSTEM_PROMPT`, `INFO_AGENT_RECENT_MESSAGES_WINDOW`, `INFO_AGENT_TOKEN_BUDGET`, `INFO_AGENT_SUMMARY_TOKEN_BUDGET`, `INFO_AGENT_MESSAGES_TO_SUMMARIZE`, `INFO_AGENT_SUMMARIZATION_PROMPT_TOKENS`, `INFO_AGENT_MESSAGE_SUMMARY_CHAR_LIMIT`
- Calendar: `CALENDAR_ID`, `DEFAULT_MEETING_DURATION_MINUTES`, `TIMEZONE`, `GOOGLE_CALENDAR_CREDENTIALS_FILE`
- Shared: `OLLAMA_BASE_URL`, `REDIS_URL`, `LOG_LEVEL`, `HOST`, `PORT`
- Edge: `WAHA_API_KEY`

## Setup
```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy example env
cp .env.example .env
# Edit .env as needed (Ollama base URL, Redis, etc)
```

Ensure Ollama is running and models are pulled:
```bash
ollama pull llama3.1
ollama pull llama2.1
```

## Running the WAHA Adapter
```bash
uvicorn convohub.waha_adapter.main:app --host 0.0.0.0 --port 8080 --reload
```

## Webhook Example
```bash
curl -X POST http://localhost:8080/webhook \
  -H "Content-Type: application/json" \
  -H "X-API-Key: changeme" \
  -d '{"from_number":"123456","message":"Can you schedule a meeting tomorrow?"}'
```

## Tool Routing Logic
The Orchestrator prompt outputs either a normal answer or a directive beginning with `TOOL:`. If `TOOL:info_agent:<query>` is produced, the FAQ agent runs. If `TOOL:calendar_scheduler:<query>` is produced, the scheduler runs.

## Extending
Add new tools by creating an agent module returning a tool dict with `name`, `description`, and `callable`, then include it in `orchestrator.py`.

## License
MIT
