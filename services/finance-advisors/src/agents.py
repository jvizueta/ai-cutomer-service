from typing import Dict
from typing_extensions import Literal
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langgraph.graph import MessagesState
from langgraph.types import Command

from .config import settings

# Configure the Ollama chat model (local LLM)
model = ChatOllama(model=settings.ollama_model, base_url=settings.ollama_base_url)

# Tools that enable cross-agent handoffs (as per the article's concept)
@tool
def ask_tax_advisor() -> str:
    """Use this tool to transfer the question to the Tax Advisor if investment advice needs tax clarification."""
    return "Passing to Tax Advisor"

@tool
def ask_finance_advisor() -> str:
    """Use this tool to transfer the question to the Finance Advisor if tax advice needs investment insight."""
    return "Passing to Finance Advisor"


def finance_advisor(state: MessagesState) -> Command[Literal["tax_advisor", "__end__"]]:
    """
    Finance Agent:
    - Gives investment advice.
    - If tax concerns arise, it uses the 'ask_tax_advisor' tool to route the query.
    """
    system_prompt = (
        "You are a Finance Advisor. Recommend investment strategies. "
        "If tax concerns arise, use the 'ask_tax_advisor' tool."
    )
    messages = [{ "role": "system", "content": system_prompt }] + state["messages"]
    ai_msg = model.bind_tools([ask_tax_advisor]).invoke(messages)

    # If the model called a tool, we interpret it as a request to switch to the other agent
    if getattr(ai_msg, "tool_calls", []):
        tool_call_id = ai_msg.tool_calls[-1]["id"]
        tool_msg: Dict = {
            "role": "tool",
            "content": "Successfully transferred",
            "tool_call_id": tool_call_id,
        }
        return Command(goto="tax_advisor", update={"messages": [ai_msg, tool_msg]})

    # Otherwise, continue with the response generated
    return { "messages": [ai_msg] }


def tax_advisor(state: MessagesState) -> Command[Literal["finance_advisor", "__end__"]]:
    """
    Tax Agent:
    - Provides tax advice.
    - If investment guidance is needed, it uses the 'ask_finance_advisor' tool to route the query.
    """
    system_prompt = (
        "You are a Tax Advisor. Provide tax advice. "
        "If investment guidance is needed, use the 'ask_finance_advisor' tool."
    )
    messages = [{ "role": "system", "content": system_prompt }] + state["messages"]
    ai_msg = model.bind_tools([ask_finance_advisor]).invoke(messages)

    if getattr(ai_msg, "tool_calls", []):
        tool_call_id = ai_msg.tool_calls[-1]["id"]
        tool_msg: Dict = {
            "role": "tool",
            "content": "Successfully transferred",
            "tool_call_id": tool_call_id,
        }
        return Command(goto="finance_advisor", update={"messages": [ai_msg, tool_msg]})

    return { "messages": [ai_msg] }
