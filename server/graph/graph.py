from langgraph.graph import StateGraph, END

from .state import MessageGraph
from .consts import REFLECT, GENERATE
from .nodes import generation_node, reflection_node
from .edegs import should_continue


def build_graph():
    """Build and compile the LangGraph workflow."""
    builder = StateGraph(state_schema=MessageGraph)

    builder.add_node(GENERATE, generation_node)
    builder.set_entry_point(GENERATE)

    builder.add_node(REFLECT, reflection_node)

    builder.add_conditional_edges(GENERATE, should_continue, path_map={END: END, REFLECT: REFLECT})
    builder.add_conditional_edges(REFLECT, should_continue, path_map={END: END, REFLECT: REFLECT})

    graph = builder.compile()
    return graph


# Create the graph instance
graph = build_graph()


def print_graph():
    """Print the graph visualization in mermaid format."""
    print(graph.get_graph().draw_mermaid())

