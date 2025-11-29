"""
Edges package for LangGraph edge/conditional logic.
Contains routing and conditional edge functions.
"""

from langgraph.graph import END
from ..state import MessageGraph
from ..consts import REFLECT


def should_continue(state: MessageGraph) -> str:
    print(state["messages"][-1].content)
    print("\nAre you happy with the recipe? (y/n)")
    return END if input() == "y" else REFLECT


__all__ = ["should_continue"]
