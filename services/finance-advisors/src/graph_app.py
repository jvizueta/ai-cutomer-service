from langgraph.graph import StateGraph, START
from langgraph.graph import MessagesState

from .agents import finance_advisor, tax_advisor

def build_graph():
    graph = StateGraph(MessagesState)
    graph.add_node("finance_advisor", finance_advisor)
    graph.add_node("tax_advisor", tax_advisor)
    graph.add_edge(START, "finance_advisor")
    app = graph.compile()
    return app
