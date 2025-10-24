# WAHA Integrator

## Introduction
WAHA Integrator is a microservice that acts as a bridge between WhatsApp (via the WAHA API) and internal AI-powered services. It receives messages from WhatsApp users, forwards them to the appropriate AI agent (such as info-agent), and returns the agent's response back to the user. This enables seamless conversational AI experiences on WhatsApp using custom LLM backends.

## Features
- Integrates WhatsApp messaging with internal AI agents
- Forwards user questions to info-agent and other services
- Returns AI-generated responses to WhatsApp users
- Configurable via environment variables
- Built with FastAPI for easy extensibility

## Requirements
- Python 3.10+
- WAHA API access
- Internal AI agent endpoints (e.g., info-agent)

## Quickstart
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Configure your `.env` file with WAHA and agent endpoints.
3. Run the service:
   ```bash
   uvicorn app.main:app --reload
   ```

## License
MIT
