from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from .models import AskReq, AskResponse
from .services.ai_service import AIService
from .config import settings
import logging

# Configure logging
logger = logging.getLogger(__name__)

app = FastAPI(title="counter-agent AI Agent", version="0.1.0")

# Initialize services
ai_service = AIService()

@app.get("/healthz")
async def healthz():
    """Health check endpoint"""
    return {
        "ok": True,
        "ai_service_available": ai_service.is_available(),
        "model": settings.lc_model
    }

@app.post("/ask", response_model=AskResponse)
async def ask(req: AskReq):
    """Generate AI response for a given question"""
    logger.info(f"Received question: {req.question[:100]}...")
    
    answer = await ai_service.generate_response(req.question, req.language)
    
    return AskResponse(answer=answer)

@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "app": "Counter Agent",
        "version": "0.1.0",
        "model": settings.lc_model,
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