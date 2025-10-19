import logging
import httpx
from ..config import settings

logger = logging.getLogger(__name__)

class AIService:
    """Service for handling AI/LLM interactions with Ollama"""

    def __init__(self):
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_model

    async def generate_response(self, question: str, language: str = "en") -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": question}
            ]
        }
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(f"{self.base_url}/v1/chat/completions", json=payload)
                response.raise_for_status()
                data = response.json()
                # Ollama returns choices[0].message.content
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Ollama API error: {e}")
            return "[Error: Unable to get response from Ollama LLM]"

    def is_available(self) -> bool:
        try:
            resp = httpx.get(f"{self.base_url}/v1/models", timeout=5)
            return resp.status_code == 200
        except Exception:
            return False
