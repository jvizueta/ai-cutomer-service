import logging
import httpx
from typing import Optional
from ..config import settings

logger = logging.getLogger(__name__)

class CounterAgentService:
    """Service for communicating with counter-agent AI Agent"""
    
    def __init__(self):
        self.base_url = settings.counter_agent_base_url.rstrip('/')
        
        if not self.base_url:
            logger.error("counter_agent_base_url not configured")
    
    async def ask(self, question: str, language: str = "en") -> str:
        """Ask question to counter-agent AI Agent"""
        try:
            payload = {
                "question": question,
                "language": language
            }
            
            timeout = httpx.Timeout(settings.response_timeout)
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    f"{self.base_url}/ask",
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("answer", "No response from AI")
                    logger.info(f"Got AI response for question: {question[:50]}...")
                    return answer
                else:
                    logger.error(f"counter-agent AI service error: {response.status_code} - {response.text}")
                    return "Sorry, the AI service is temporarily unavailable."
                    
        except httpx.TimeoutException:
            logger.error("Timeout calling counter-agent AI service")
            return "Sorry, the AI service took too long to respond."
        except httpx.ConnectError:
            logger.error(f"Connection error to counter-agent AI at {self.base_url}")
            return "Sorry, I cannot connect to the AI service right now."
        except Exception as e:
            logger.error(f"Error calling counter-agent AI service: {str(e)}")
            return "Sorry, there was an error processing your request."
    
    async def health_check(self) -> bool:
        """Check if counter-agent AI service is healthy"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/healthz")
                return response.status_code == 200
        except Exception as e:
            logger.error(f"counter-agent AI health check failed: {str(e)}")
            return False
    
    def is_available(self) -> bool:
        """Check if counter-agent service configuration is available"""
        return bool(self.base_url)