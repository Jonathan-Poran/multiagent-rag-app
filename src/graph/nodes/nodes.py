"""
Node functions for LangGraph workflow.
Contains generation and reflection node implementations.
"""

import json
from langchain_core.messages import HumanMessage, AIMessage
from ..chains import generation_chain, reflection_chain
from ..state import MessageGraph


def generation_node(state: MessageGraph):
    """
    Generation node that extracts topic and details from user's social media content request.
    
    Args:
        state: The current graph state containing messages.
    
    Returns:
        dict: Updated state with the structured JSON containing topic and details.
    """
    result = generation_chain.invoke({"messages": state["messages"]})
    
    # Convert the structured output to JSON string
    content_structure = {
        "topic": result.topic,
        "details": result.details
    }
    json_response = json.dumps(content_structure, ensure_ascii=False, indent=2)
    
    # Create an AIMessage with the JSON structure
    ai_message = AIMessage(content=json_response)
    
    return {"messages": [ai_message]}


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

