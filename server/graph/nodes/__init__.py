"""
Nodes package for LangGraph node implementations.
Contains generation and reflection node functions.
"""

from ..chains import generation_chain, reflection_chain
from langchain_core.messages import HumanMessage
from ..state import MessageGraph


def generation_node(state: MessageGraph):
    result = generation_chain.invoke({"messages": state["messages"]})
    return {"messages": [result]}


def reflection_node(state: MessageGraph):
    result = reflection_chain.invoke({"messages": state["messages"]})
    return {"messages": [HumanMessage(result.content)]}  # this message annotated as HumanMessage because its simulates the user's response to the reflection


__all__ = ["generation_node", "reflection_node"]
