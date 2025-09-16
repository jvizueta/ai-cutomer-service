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
**Tip:**  
If you don't have `pytest` installed, add it to your `requirements.txt` or install it with `pip install pytest`.