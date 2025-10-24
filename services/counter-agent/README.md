# Counter Agent

## Introduction
Counter Agent is a LangChain-based project that uses OpenAI for natural language processing and question answering. Counter Agent answers general questions related to the customer service

## Setup (Python Virtual Environment)

1. **Create and activate a virtual environment:**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Install dependencies:**

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Run tests (if you have tests):**

   ```bash
   pytest
   ```

4. **Run the application locally:**

   ```bash
   uvicorn app.main:app --reload
   ```

5. **Deactivate the virtual environment when done:**
 
   ```bash
   deactivate
   ```

---

## Manual Testing

You can manually test the counter-agent app using `curl` or any HTTP client (like Postman or httpie):

### 1. **Health Check**

```bash
curl http://localhost:8000/healthz
```

Expected response:
```json
{"ok": true}
```

### 2. **Ask Endpoint**

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is LangChain?"}'
```

Expected response (if LangChain is installed and configured):
```json
{"answer": "..."}
```
If LangChain is not installed, you'll get a fallback message.

---

## Building the Docker Image Manually

To build the counter-agent Docker image locally, run:

```bash
docker build -t counter-agent:latest .
```

To run the container locally (mapping port 8000):

```bash
docker run --env-file .env -p 8000:8000 counter-agent:latest
```

---

**Tip:**  
If you don't have `pytest` installed, add it to your `requirements.txt` or install it with `pip install pytest`.