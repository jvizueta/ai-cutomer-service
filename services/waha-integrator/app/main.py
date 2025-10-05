from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from .models import WAHAWebhookReq
from .services.waha_service import WAHAService
from .services.counter_agent_service import CounterAgentService
from .config import settings
import logging

logger = logging.getLogger(__name__)

app = FastAPI(title="WAHA Integrator", version="0.1.0")
waha_service = WAHAService()
counter_agent_service = CounterAgentService()

@app.get("/healthz")
async def healthz():
    return {
        "ok": True,
        "waha_service_available": waha_service.is_available(),
        "counter_agent_service_available": counter_agent_service.is_available(),
        "default_language": settings.default_language  # Show current config
    }

@app.post("/webhook")
async def waha_webhook(req: WAHAWebhookReq):
    logger.info(f"Full request: {req.json()}")
    logger.info(f"Received webhook event: {req.event} for session {req.session}")

    # Try to extract message from payload.data if present
    payload = req.payload
    data = payload.get("data", {})
    message = data.get("body") or payload.get("body")
    chat_id = data.get("from") or payload.get("from")
    msg_type = data.get("type") or payload.get("type")

    # Only process chat/text messages
    if msg_type != "chat" or not message or not chat_id:
        logger.info("Ignoring non-chat event or missing message/chat_id")
        return {"status": "ignored"}

    logger.info(f"Processing message from {chat_id}: {message[:100]}...")

    ai_response = await counter_agent_service.ask(message, language=settings.default_language)
    logger.info(f"AI response: {ai_response[:100]}...")

    result = await waha_service.send_text(req.session, chat_id, ai_response)
    logger.info(f"WAHA send result: {result}")

    if result:
        logger.info(f"Successfully sent response to {chat_id}")
        return {"status": "sent", "message": ai_response}
    else:
        logger.error(f"Failed to send response to {chat_id}")
        return {"status": "error", "details": "Failed to send via WAHA"}

@app.get("/")
async def root():
    return {
        "app": "WAHA Integrator", 
        "version": "0.1.0",
        "default_language": settings.default_language,
        "endpoints": ["/webhook", "/healthz"]
    }