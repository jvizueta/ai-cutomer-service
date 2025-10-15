import logging
from typing import Optional
from ..config import settings

try:
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import HumanMessage
    from langchain_redis import RedisChatMessageHistory
    from langchain.memory import ConversationBufferMemory
except ImportError:
    ChatOpenAI = None
    HumanMessage = None
    RedisChatMessageHistory = None
    ConversationBufferMemory = None

logger = logging.getLogger(__name__)

class AIService:
    """Service for handling AI/LLM interactions with Redis-based memory"""

    def __init__(self, session_id: str = "default"):
        self.api_key = settings.openai_api_key or settings.openrouter_api_key
        self.model_name = settings.lc_model
        self.temperature = settings.lc_temperature
        self.redis_url = settings.redis_url
        self.session_id = session_id

        if not self.api_key:
            logger.warning("No API key found for AI service")

        if not self.redis_url:
            logger.warning("No Redis URL found for AI service; memory will be disabled")
        else:
            logger.info(f"Using Redis URL: {self.redis_url}")

        self._llm = None
        self._memory = None

    @property
    def llm(self):
        """Lazy initialization of LLM client"""
        if self._llm is None and ChatOpenAI is not None and self.api_key:
            self._llm = ChatOpenAI(
                api_key=self.api_key,
                model=self.model_name,
                temperature=self.temperature
            )
        return self._llm

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
            if self.llm is None:
                if ChatOpenAI is None:
                    return f"Echo: {question} (LangChain not available)"
                elif not self.api_key:
                    return "AI service unavailable (no API key configured)"
                else:
                    return "AI service unavailable (initialization failed)"

            # Construct prompt based on language
            logger.info(f"Generating response for question: {question[:50]} in language: {language}")
            if language.lower() in ["es", "spanish", "español"]:
                prompt = f"Responde brevemente en español: {question}"
            else:
                prompt = f"Answer briefly in {language}: {question}"

            logger.debug(f"Using prompt: {prompt}")
            message = HumanMessage(content=prompt)
            logger.debug("Sending message to LLM...")
            response = await self.llm.ainvoke([message])
            logger.debug("Received response from LLM")
            
            # Save to Redis memory
            logger.debug("Saving conversation to Redis memory")
            if self.memory is not None:
                try:
                    logger.debug("Memory is available, saving context")
                    self.memory.save_context({"input": prompt}, {"output": response.content})
                    logger.debug("Successfully saved conversation to Redis memory")
                except Exception as memory_error:
                    logger.warning(f"Failed to save conversation to Redis memory: {str(memory_error)}")
                    # Continue without failing the whole request

            logger.info(f"Generated AI response for question: {question[:50]}...")
            logger.debug(f"AI response: {response.content}")
            return response.content

        except Exception as e:
            logger.error(f"Error generating AI response: {str(e)}")
            return f"Sorry, I encountered an error processing your request."

    def is_available(self) -> bool:
        """Check if AI service is available"""
        return self.llm is not None