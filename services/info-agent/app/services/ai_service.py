import logging

import httpx
from ..config import settings

logger = logging.getLogger(__name__)

try:
    from langchain_redis import RedisChatMessageHistory
    from langchain.memory import ConversationBufferMemory
except ImportError:
    RedisChatMessageHistory = None
    ConversationBufferMemory = None
    logger.warning("langchain or langchain-redis not installed; Redis memory functionality will be disabled")




class AIService:
    """Service for handling AI/LLM interactions with Ollama and Redis-based memory"""

    def __init__(self, session_id: str = "default"):
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_model
        self.temperature = settings.ollama_temperature
        self.redis_url = settings.redis_url
        self.session_id = session_id
        self._memory = None

        if not self.base_url:
            logger.warning("No Ollama base URL found for AI service")
        if not self.redis_url:
            logger.warning("No Redis URL found for AI service; memory will be disabled")
        else:
            logger.info(f"Using Redis URL: {self.redis_url}")

    @property
    def memory(self):
        """Lazy initialization of Redis-based memory"""
        if self._memory is None and RedisChatMessageHistory is not None and ConversationBufferMemory is not None:
            try:
                logger.info("Initializing Redis-based memory")
                logger.debug(f"Redis URL: {self.redis_url}")
                logger.debug(f"Session ID: {self.session_id}")
                chat_history = RedisChatMessageHistory(
                    session_id=self.session_id,
                    redis_url=self.redis_url
                )
                logger.info("Redis chat history initialized")
                self._memory = ConversationBufferMemory(
                    memory_key="chat_history",
                    chat_memory=chat_history,
                    return_messages=True
                )
                logger.info("Conversation buffer memory initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Redis memory: {str(e)}")
                logger.warning("Continuing without memory functionality")
                self._memory = None
        return self._memory

    async def generate_response(self, question: str, language: str = "en") -> str:
        """Generate AI response for a given question and store in Redis memory"""
        try:
            logger.info(f"Generating response for question: {question[:50]} in language: {language}")
            # Construct prompt based on language
            if language.lower() in ["es", "spanish", "español"]:
                prompt = f"Responde brevemente en español: {question}"
            else:
                prompt = f"Answer briefly in {language}: {question}"

            logger.debug(f"Using prompt: {prompt}")

            payload = {
                "model": self.model,
                "temperature": self.temperature,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
            logger.debug(f"Payload for Ollama: {payload}")

            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(f"{self.base_url}/v1/chat/completions", json=payload)
                response.raise_for_status()
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                logger.debug("Received response from Ollama")

            # Save to Redis memory (use save_context like counter-agent)
            logger.debug("Saving conversation to Redis memory")
            if self.memory is not None:
                try:
                    logger.debug("Memory is available, saving context")
                    self.memory.save_context({"input": prompt}, {"output": content})
                    logger.debug("Successfully saved conversation to Redis memory")
                except Exception as memory_error:
                    logger.warning(f"Failed to save conversation to Redis memory: {str(memory_error)}")
            else:
                logger.debug("No memory available; skipping save to Redis")
            logger.info(f"Generated AI response for question: {question[:50]}...")
            logger.debug(f"AI response: {content}")
            return content

        except Exception as e:
            logger.error(f"Error generating AI response: {str(e)}")
            return "[Error: Unable to get response from Ollama LLM]"

    def is_available(self) -> bool:
        try:
            resp = httpx.get(f"{self.base_url}/v1/models", timeout=5)
            return resp.status_code == 200
        except Exception:
            return False
