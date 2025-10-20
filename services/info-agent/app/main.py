import os
from dotenv import load_dotenv
load_dotenv()

import logging
from fastapi import FastAPI
from .models import AskReq, AskResponse
from .services.ai_service import AIService
from .config import settings

logger = logging.getLogger(__name__)

app = FastAPI(title="info-agent AI Agent", version="0.1.0")

ai_service = AIService()

@app.get("/healthz")
async def healthz():
    return {
        "ok": True,
        "ai_service_available": ai_service.is_available(),
        "model": settings.ollama_model
    }

@app.post("/ask", response_model=AskResponse)
async def ask(req: AskReq):
    logger.info(f"Received question: {req.question[:100]}...")
    answer = await ai_service.generate_response(req.question, req.language)
    return AskResponse(answer=answer)

@app.get("/")
async def root():
    return {
        "app": "Info Agent",
        "version": "0.1.0",
        "model": settings.ollama_model,
        "ai_available": ai_service.is_available(),
        "endpoints": ["/ask", "/healthz"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower()
    )
