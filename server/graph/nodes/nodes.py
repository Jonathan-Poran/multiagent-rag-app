"""
Node functions for LangGraph workflow.
Contains generation and reflection node implementations.
"""

from langchain_core.messages import HumanMessage
from ..chains import generation_chain, reflection_chain
from ..state import MessageGraph


def generation_node(state: MessageGraph):
    """
    Generation node that creates a recipe based on available ingredients.
    
    Args:
        state: The current graph state containing messages.
    
    Returns:
        dict: Updated state with the generated recipe message.
    """
    result = generation_chain.invoke({"messages": state["messages"]})
    return {"messages": [result]}


def reflection_node(state: MessageGraph):
    """
    Reflection node that improves or reflects on the generated recipe.
    
    Args:
        state: The current graph state containing messages.
    
    Returns:
        dict: Updated state with the reflected recipe message.
    """
    result = reflection_chain.invoke({"messages": state["messages"]})
    # This message is annotated as HumanMessage because it simulates the user's response to the reflection
    return {"messages": [HumanMessage(result.content)]}

