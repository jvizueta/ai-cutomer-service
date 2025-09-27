from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from pydantic import BaseModel
import os

# Minimal LangChain agent (OpenAI-compatible). Install: langchain, langchain-openai
try:
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import HumanMessage
except Exception:
    ChatOpenAI = None
    HumanMessage = None

app = FastAPI(title="Lyra", version="0.1.0")


class AskReq(BaseModel):
    question: str


@app.get("/healthz")
async def healthz():
    return {"ok": True}


@app.post("/ask")
async def ask(req: AskReq):
    # Prefer OPENAI_API_KEY; support OPENROUTER_API_KEY as fallback
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENROUTER_API_KEY")
    model_name = os.getenv("LC_MODEL", "gpt-4o-mini")

    if ChatOpenAI is None:
        return {"answer": f"Hello, {req.question}. (LangChain not installed in image)"}

    llm = ChatOpenAI(api_key=api_key, model=model_name, temperature=0.2)
    msg = await llm.ainvoke([HumanMessage(content=f"Answer briefly: {req.question}")])
    return {"answer": msg.content}