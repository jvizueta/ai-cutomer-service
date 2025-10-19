import httpx
import logging
from ..config import settings

logger = logging.getLogger(__name__)

class InfoAgentService:
    """Adapter for calling the info-agent service from waha-integrator."""

    def __init__(self):
        self.base_url = settings.info_agent_url  # e.g. "http://info-agent:8000"

    async def ask(self, question: str, language: str = "en") -> str:
        payload = {"question": question, "language": language}
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(f"{self.base_url}/ask", json=payload)
                response.raise_for_status()
                data = response.json()
                # Adapt to your info-agent response format
                return data.get("answer") or data.get("response") or str(data)
        except Exception as e:
            logger.error(f"Error calling info-agent: {e}")
            return "[Error: Unable to get response from info-agent]"

    def is_available(self) -> bool:
        try:
            resp = httpx.get(f"{self.base_url}/healthz", timeout=5)
            return resp.status_code == 200
        except Exception:
            return False
