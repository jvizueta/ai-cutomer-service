from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from .models import WAHAWebhookReq
from .services.waha_service import WAHAService
from .services.lyra_service import LyraService
from .config import settings
import logging

logger = logging.getLogger(__name__)

app = FastAPI(title="WAHA Integration", version="0.1.0")
waha_service = WAHAService()
lyra_service = LyraService()

@app.get("/healthz")
async def healthz():
    return {
        "ok": True,
        "waha_service_available": waha_service.is_available(),
        "lyra_service_available": lyra_service.is_available(),
        "default_language": settings.default_language  # Show current config
    }

@app.post("/webhook")
async def waha_webhook(req: WAHAWebhookReq):
    if req.event != "message" or req.payload.get("type") != "text":
        return {"status": "ignored"}
    
    message = req.payload.get("body", "").strip()
    chat_id = req.payload.get("from")
    
    if not message or not chat_id:
        return {"status": "ignored"}
    
    logger.info(f"Processing message from {chat_id}: {message[:100]}...")
    
    # Get AI response from lyra service - USE CONFIG VALUE
    ai_response = await lyra_service.ask(message, language=settings.default_language)
    
    # Send back via WAHA
    result = await waha_service.send_text(req.session, chat_id, ai_response)
    
    if result:
        logger.info(f"Successfully sent response to {chat_id}")
        return {"status": "sent", "message": ai_response}
    else:
        logger.error(f"Failed to send response to {chat_id}")
        return {"status": "error", "details": "Failed to send via WAHA"}

@app.get("/")
async def root():
    return {
        "app": "WAHA Integration", 
        "version": "0.1.0",
        "default_language": settings.default_language,
        "endpoints": ["/webhook", "/healthz"]
    }