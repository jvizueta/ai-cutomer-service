import logging

import httpx
from ..config import settings

try:
    from langchain_redis import RedisChatMessageHistory
    from langchain.memory import ConversationBufferMemory
except ImportError:
    RedisChatMessageHistory = None
    ConversationBufferMemory = None

logger = logging.getLogger(__name__)


class AIService:
    """Service for handling AI/LLM interactions with Ollama and Redis-based memory"""

    def __init__(self, session_id: str = "default"):
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_model
        self.temperature = settings.ollama_temperature
        self.redis_url = settings.redis_url
        self.session_id = session_id
        self._memory = None

    @property
    def memory(self):
        """Lazy initialization of Redis-based memory"""
        if self._memory is None and RedisChatMessageHistory is not None and ConversationBufferMemory is not None and self.redis_url:
            try:
                logger.info("Initializing Redis-based memory")
                chat_history = RedisChatMessageHistory(
                    session_id=self.session_id,
                    url=self.redis_url
                )
                self._memory = ConversationBufferMemory(
                    memory_key="chat_history",
                    chat_memory=chat_history,
                    return_messages=True
                )
            except Exception as e:
                logger.error(f"Failed to initialize Redis memory: {e}")
                self._memory = None
        return self._memory

    async def generate_response(self, question: str, language: str = "en") -> str:
        payload = {
            "model": self.model,
            "temperature": self.temperature,
            "messages": [
                {"role": "user", "content": question}
            ]
        }
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(f"{self.base_url}/v1/chat/completions", json=payload)
                response.raise_for_status()
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                # Store message in Redis memory if available
                if self.memory:
                    try:
                        self.memory.chat_memory.add_user_message(question)
                        self.memory.chat_memory.add_ai_message(content)
                    except Exception as e:
                        logger.error(f"Failed to store messages in Redis: {e}")
                return content
        except Exception as e:
            logger.error(f"Ollama API error: {e}")
            return "[Error: Unable to get response from Ollama LLM]"

    def is_available(self) -> bool:
        try:
            resp = httpx.get(f"{self.base_url}/v1/models", timeout=5)
            return resp.status_code == 200
        except Exception:
            return False
