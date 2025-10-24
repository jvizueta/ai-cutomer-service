from langchain_core.messages import convert_to_messages
from .graph_app import build_graph

def pretty_print_messages(update):
    # Mirrors the 'pretty print' loop shown in the article
    if isinstance(update, tuple):
        ns, update = update
        # skip parent graph updates
        if len(ns) == 0:
            return
        graph_id = ns[-1].split(":")[0]
        print(f"Update from subgraph {graph_id}:\n")

    for node_name, node_update in update.items():
        print(f"Update from node {node_name}:\n")
        # print(f"Node messages: {node_update['messages']}\n")
        # print(f"Messages:")
        for m in convert_to_messages(node_update["messages"]):
            # print(" - ", end="")
            try:
                m.pretty_print()
            except Exception:
                print(m)
        print("")

def main():
    app = build_graph()
    print("Graph compiled. Streaming updates...\n")

    for chunk in app.stream(
        { "messages": [("user", "suggest how to invest money")] }
    ):
        pretty_print_messages(chunk)

if __name__ == "__main__":
    main()
