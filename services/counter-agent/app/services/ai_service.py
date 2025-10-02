import logging
from typing import Optional
from ..config import settings

try:
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import HumanMessage
except ImportError:
    ChatOpenAI = None
    HumanMessage = None

logger = logging.getLogger(__name__)

class AIService:
    """Service for handling AI/LLM interactions"""
    
    def __init__(self):
        self.api_key = settings.openai_api_key or settings.openrouter_api_key
        self.model_name = settings.lc_model
        self.temperature = settings.lc_temperature
        
        if not self.api_key:
            logger.warning("No API key found for AI service")
        
        self._llm = None
    
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
    
    async def generate_response(self, question: str, language: str = "en") -> str:
        """Generate AI response for a given question"""
        try:
            if self.llm is None:
                if ChatOpenAI is None:
                    return f"Echo: {question} (LangChain not available)"
                elif not self.api_key:
                    return "AI service unavailable (no API key configured)"
                else:
                    return "AI service unavailable (initialization failed)"
            
            # Construct prompt based on language
            if language.lower() in ["es", "spanish", "español"]:
                prompt = f"Responde brevemente en español: {question}"
            else:
                prompt = f"Answer briefly in {language}: {question}"
            
            message = HumanMessage(content=prompt)
            response = await self.llm.ainvoke([message])
            
            logger.info(f"Generated AI response for question: {question[:50]}...")
            return response.content
            
        except Exception as e:
            logger.error(f"Error generating AI response: {str(e)}")
            return f"Sorry, I encountered an error processing your request."
    
    def is_available(self) -> bool:
        """Check if AI service is available"""
        return self.llm is not None