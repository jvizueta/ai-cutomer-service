# Lyra

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

You can manually test the Lyra app using `curl` or any HTTP client (like Postman or httpie):

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

**Tip:**  
If you don't have `pytest` installed, add it to your `requirements.txt` or install it with `pip install pytest`.