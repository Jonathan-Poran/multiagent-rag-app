"""
Conversation state management for chat engine.
Stores conversation states in memory.
"""

from langchain_core.messages import HumanMessage
from server.graph.state import MessageGraph
from server.config.logger import get_logger

logger = get_logger("Conversation")

# Global dictionary to store conversation states
# Key: conversation_id (str), Value: MessageGraph state
_conversation_states: dict[str, MessageGraph] = {}


def get_or_create_conversation_state(conversation_id: str) -> MessageGraph:
    """
    Get existing conversation state or create a new one.
    
    Args:
        conversation_id: Unique identifier for the conversation.
    
    Returns:
        MessageGraph: The conversation state with messages list.
    """
    if conversation_id not in _conversation_states:
        # Create new conversation state
        _conversation_states[conversation_id] = {"messages": []}
        logger.info(f"Created new conversation state for ID: {conversation_id}")
    else:
        logger.debug(f"Retrieved existing conversation state for ID: {conversation_id}")
    
    return _conversation_states[conversation_id]


def reset_conversation(conversation_id: str) -> None:
    """
    Reset a conversation by clearing its messages.
    
    Args:
        conversation_id: Unique identifier for the conversation.
    """
    _conversation_states[conversation_id] = {"messages": []}
    logger.info(f"Reset conversation state for ID: {conversation_id}")


def add_user_message(conversation_id: str, user_text: str) -> MessageGraph:
    """
    Add a user message to the conversation state.
    
    Args:
        conversation_id: Unique identifier for the conversation.
        user_text: The user's message text.
    
    Returns:
        MessageGraph: Updated conversation state.
    """
    state = get_or_create_conversation_state(conversation_id)
    user_message = HumanMessage(content=user_text)
    state["messages"].append(user_message)
    logger.info(f"Added user message to conversation {conversation_id}")
    return state


def update_conversation_state(conversation_id: str, new_state: MessageGraph) -> None:
    """
    Update the conversation state after graph execution.
    
    Args:
        conversation_id: Unique identifier for the conversation.
        new_state: The updated state from the graph.
    """
    _conversation_states[conversation_id] = new_state
    logger.debug(f"Updated conversation state for ID: {conversation_id}")

