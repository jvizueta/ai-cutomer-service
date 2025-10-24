import logging
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from ..config import settings
from ..orchestrator import Orchestrator

logger = logging.getLogger(__name__)
app = FastAPI(title="WAHA Adapter")

orchestrator = Orchestrator()

class WebhookPayload(BaseModel):
    from_number: str
    message: str

@app.get("/healthz")
async def healthz():
    return {"ok": True}

@app.post("/webhook")
async def webhook(payload: WebhookPayload, x_api_key: str = Header(None)):
    if settings.WAHA_API_KEY and x_api_key != settings.WAHA_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    user_query = payload.message.strip()
    logger.info(f"Received webhook from {payload.from_number}: {user_query}")
    response_text = orchestrator.invoke(user_query)
    return {"answer": response_text}
