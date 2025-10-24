import logging
from typing import List, Dict, Any, Callable
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate
from langchain_community.chat_models import ChatOllama
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor
from .config import settings
from .agents.info_agent import info_agent_tool
from .agents.calendar_scheduler import calendar_scheduler_tool

logger = logging.getLogger(__name__)

# Define the shared state for the graph
class OrchestratorState(dict):
    """State container. Holds messages and the last tool used."""
    messages: List[Dict[str, Any]]
    last_tool: str | None


def build_orchestrator_graph():
    # Instantiate tool definitions
    tools = [info_agent_tool(), calendar_scheduler_tool()]
    tool_map = {t["name"]: t for t in tools}
    tool_executor = ToolExecutor({name: t["callable"] for name, t in tool_map.items()})

    llm = ChatOllama(
        base_url=settings.OLLAMA_BASE_URL,
        model=settings.SUPERVISOR_MODEL,
        temperature=settings.SUPERVISOR_TEMPERATURE,
    )

    system_prompt = (
        "You are the Orchestrator. Decide which tool to call based on the user's intent:\n"
        "- Use info_agent for FAQs or general company/customer information.\n"
        "- Use calendar_scheduler for availability checking and meeting scheduling.\n"
        "Output: If a tool is needed, respond with: TOOL:<tool_name>:<user_query>. Otherwise answer directly."
    )
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}")
    ])

    def router(state: OrchestratorState):
        user_input = state.get("user_input", "")
        chain = prompt | llm
        resp = chain.invoke({"input": user_input})
        text = resp.content.strip()
        if text.startswith("TOOL:"):
            # parse TOOL:tool_name:query
            try:
                _, tool_name, query = text.split(":", 2)
                if tool_name in tool_map:
                    result = tool_executor.invoke({"tool": tool_name, "query": query})
                    return {"messages": state.get("messages", []) + [
                        {"role": "assistant", "content": f"[Tool {tool_name} result] {result}"}
                    ], "last_tool": tool_name}
            except Exception as e:
                return {"messages": state.get("messages", []) + [
                    {"role": "assistant", "content": f"[Routing error] {e}"}
                ]}
        # No tool call, direct answer
        return {"messages": state.get("messages", []) + [
            {"role": "assistant", "content": text}
        ], "last_tool": None}

    graph = StateGraph(OrchestratorState)
    graph.add_node("router", router)
    graph.set_entry_point("router")
    graph.set_finish_point("router")
    compiled = graph.compile()
    return compiled

class Orchestrator:
    def __init__(self):
        self.graph = build_orchestrator_graph()

    def invoke(self, user_input: str) -> str:
        state = {"user_input": user_input, "messages": []}
        result = self.graph.invoke(state)
        msgs = result.get("messages", [])
        if msgs:
            return msgs[-1]["content"]
        return "[No response]"
