# LangGraph + Ollama Multi-Agent (Based on Medium article)

This project reproduces the **Network Architecture** example from
*“Building Multi-Agent Systems with LangGraph and Ollama: Architectures, Concepts, and Code”* (Apr 11, 2025) by Diwakar Kumar.

It defines two agents (Finance Advisor and Tax Advisor) that can route between each other using tool calls,
running **locally** on Ollama via `ChatOllama`.

> Note: You need Ollama installed, running, and a compatible model (e.g. `llama3.2`) pulled.

## Quickstart

```bash
# 1) Create and activate a virtual environment (optional but recommended)
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate

# 2) Install dependencies
pip install -r requirements.txt

# 3) Ensure Ollama is running and model is available
#    Start ollama in the background and pull a model if needed:
#    ollama serve
#    ollama pull llama3.2

# 4) Set environment variables (or edit .env)
cp .env.example .env

# 5) Run the graph
python -m src.runner
```

## Files

```
.
├── requirements.txt
├── .env.example
├── .env
├── README.md
└── src
    ├── __init__.py
    ├── agents.py
    ├── config.py
    ├── graph_app.py
    └── runner.py
```

## Notes

- The code follows the article's outline: two agents with cross-handoff tools, connected via a `StateGraph`.
- If you use a different local model, update `OLLAMA_MODEL` in `.env`.
- If your Ollama server is remote, change `OLLAMA_BASE_URL` accordingly.
- For visualization (Mermaid PNG of the graph), refer to LangGraph docs—this example focuses on CLI streaming output.

## Architecture

Finance-Advisors uses a network architecture combining LangGraph and Ollama:

```
+-------------------+        +-------------------+        +-------------------+
|   User/Client     | <----> |   Finance-Agent   | <----> |     Ollama LLM    |
+-------------------+        +-------------------+        +-------------------+
                                   |
                                   v
                          +-------------------+
                          |   LangGraph Core  |
                          +-------------------+
```
- **User/Client**: Sends financial questions or requests.
- **Finance-Agent**: Orchestrates the workflow, manages context, and interacts with the LLM.
- **Ollama LLM**: Processes natural language and provides responses.
- **LangGraph Core**: Handles graph-based agent logic, memory, and tool use.

## Features
- Modular agent design for financial tasks
- Streaming and interactive responses
- Configurable via `.env` and Python config

