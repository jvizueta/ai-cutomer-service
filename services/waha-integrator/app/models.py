from pydantic import BaseModel
from typing import Dict, Any

class WAHAWebhookReq(BaseModel):
    event: str
    session: str
    payload: Dict[str, Any]