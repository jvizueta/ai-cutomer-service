from pydantic import BaseModel

class AskReq(BaseModel):
    question: str
    language: str = "en"

class AskResponse(BaseModel):
    answer: str