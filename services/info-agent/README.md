# Info-Agent

Info-Agent is an AI-powered microservice designed to provide customer engagement and information services. It leverages large language models (LLMs) via the Ollama API and supports conversation memory using Redis.

## Features
- Uses Ollama for LLM-based responses (default: Llama 3.1)
- Adaptive summarization and context windowing for efficient memory usage
- Configurable via environment variables and Kubernetes ConfigMap
- Redis integration for persistent conversation history
- FastAPI-based HTTP API

## Usage
- Deploy as a microservice in your stack
- Configure Ollama, Redis, and summarization parameters via `.env` or environment variables
- Interact with the `/ask` endpoint to get AI-powered answers

## Requirements
- Python 3.10+
- Ollama server (local or remote)
- Redis server

## Example .env
```
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=llama3.1
OLLAMA_TEMPERATURE=0.2
OLLAMA_TIMEOUT=60
REDIS_URL=redis://localhost:6379/0
SYSTEM_PROMPT=You are a customer engagement agent for a marketing agency.
DEFAULT_LANGUAGE=english
RECENT_MESSAGES_WINDOW=6
TOKEN_BUDGET=8192
SUMMARY_TOKEN_BUDGET=1000
MESSAGES_TO_SUMMARIZE=10
SUMMARIZATION_PROMPT_TOKENS=100
MESSAGE_SUMMARY_CHAR_LIMIT=600
```

## License
MIT
