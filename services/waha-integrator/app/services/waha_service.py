import logging
import httpx
from typing import Optional
from ..config import settings

logger = logging.getLogger(__name__)

class WAHAService:
    """Service for communicating with WAHA API"""
    
    def __init__(self):
        self.base_url = settings.waha_base_url.rstrip('/')
        self.api_key = settings.waha_api_key
        
        if not self.api_key:
            logger.warning("WAHA_API_KEY not configured - requests may fail")
    
    def _get_headers(self) -> dict:
        """Get headers for WAHA API requests"""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
    
    async def send_text(self, session: str, chat_id: str, text: str) -> bool:
        """Send text message via WAHA API"""
        try:
            payload = {
                "session": session,
                "chatId": chat_id,
                "text": text
            }
            
            timeout = httpx.Timeout(settings.response_timeout)
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/sendText",
                    headers=self._get_headers(),
                    json=payload
                )
                
                if response.status_code == 200:
                    logger.info(f"Successfully sent message to {chat_id}")
                    return True
                else:
                    logger.error(f"Failed to send message: {response.status_code} - {response.text}")
                    return False
                    
        except httpx.TimeoutException:
            logger.error(f"Timeout sending message to WAHA")
            return False
        except httpx.ConnectError:
            logger.error(f"Connection error to WAHA at {self.base_url}")
            return False
        except Exception as e:
            logger.error(f"Error sending message via WAHA: {str(e)}")
            return False
    
    async def get_sessions(self) -> Optional[list]:
        """Get list of WAHA sessions"""
        try:
            timeout = httpx.Timeout(settings.response_timeout)
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/sessions",
                    headers=self._get_headers()
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Failed to get sessions: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting WAHA sessions: {str(e)}")
            return None
    
    def is_available(self) -> bool:
        """Check if WAHA service configuration is available"""
        return bool(self.base_url and self.api_key)
