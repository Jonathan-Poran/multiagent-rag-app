"""
Edge functions for LangGraph conditional routing.
Contains the should_continue function that determines graph flow.
"""

from langgraph.graph import END
from ..state import MessageGraph
from ..consts import REFLECT


def should_continue(state: MessageGraph) -> str:
    """
    Determine whether to continue the graph workflow or end.
    
    Args:
        state: The current graph state containing messages.
    
    Returns:
        str: Either END or REFLECT constant to determine next step.
    """
    print(state["messages"][-1].content)
    return END
    # Note: The input() call below is commented out as it's not suitable for production
    # print("\nAre you happy with the recipe? (y/n)")
    # return END if input() == "y" else REFLECT

