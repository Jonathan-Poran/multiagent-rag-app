"""
Graph factory service for managing graph instances per conversation.
Creates a new graph instance for each conversation_id and cleans up when execution completes.
"""
from typing import TypedDict, Optional, Any
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage
from src.config.logger import get_logger
from src.dto.chat_dto import UserMessage, ChatResponse
logger = get_logger("GraphFactory")

# TypedDict for storing graphs per conversation_id
class GraphRegistry(TypedDict):
    """Registry of graphs by conversation_id."""
    pass


# Global dictionary to store graphs per conversation_id
# Key: conversation_id (str), Value: Compiled graph instance
_graph_registry: dict[str, StateGraph] = {}


def _build_graph() -> StateGraph:
    """
    Build and compile a new graph instance.
    Uses lazy imports to avoid circular dependencies.
    
    Returns:
        Any: A compiled LangGraph instance.
    """
    # Lazy imports to avoid circular dependencies
    from src.graph.nodes import topic_extraction_node, find_url_node
    from src.graph.consts import TOPIC_EXTRACTION, FIND_URL
    from src.graph.edges import route_after_topic_extraction
    from src.graph.state import MessageGraph
    
    builder = StateGraph(state_schema=MessageGraph)
    
    # Add nodes
    builder.add_node(TOPIC_EXTRACTION, topic_extraction_node)
    builder.add_node(FIND_URL, find_url_node)
    
    # Entry point
    builder.set_entry_point(TOPIC_EXTRACTION)
    
    # Conditional edges
    builder.add_conditional_edges(
        TOPIC_EXTRACTION,
        route_after_topic_extraction,
        {TOPIC_EXTRACTION: TOPIC_EXTRACTION, FIND_URL: FIND_URL}
    )
    
    # After find_url_node, end the graph
    builder.add_edge(FIND_URL, END)
    
    # Compile and return
    graph = builder.compile()
    logger.debug("Built new graph instance")

    return graph


def _get_or_create_graph(conversation_id: str) -> Any:
    """
    Get existing graph for conversation_id or create a new one.
    
    Args:
        conversation_id: Unique identifier for the conversation.
    
    Returns:
        Any: The graph instance for this conversation.
    """
    if conversation_id not in _graph_registry:
        # Create new graph instance
        _graph_registry[conversation_id] = _build_graph()
        logger.info(f"Created new graph instance for conversation_id: {conversation_id}")
    else:
        logger.debug(f"Retrieved existing graph instance for conversation_id: {conversation_id}")
    
    return _graph_registry[conversation_id]


def _delete_graph(conversation_id: str) -> None:
    """
    Delete the graph instance for a conversation_id.
    This should be called when the graph execution completes (reaches END).
    
    Args:
        conversation_id: Unique identifier for the conversation.
    """
    if conversation_id in _graph_registry:
        del _graph_registry[conversation_id]
        logger.info(f"Deleted graph instance for conversation_id: {conversation_id}")
    else:
        logger.warning(f"Attempted to delete non-existent graph for conversation_id: {conversation_id}")


def _get_graph(conversation_id: str) -> Optional[Any]:
    """
    Get the graph instance for a conversation_id without creating a new one.
    
    Args:
        conversation_id: Unique identifier for the conversation.
    
    Returns:
        Optional[Any]: The graph instance if it exists, None otherwise.
    """
    return _graph_registry.get(conversation_id)


def routeInputToGraph(req: UserMessage) -> ChatResponse:
    """
    Route the input to the appropriate graph.
    
    Args:
        req: UserMessage containing the conversation_id and text.
    
    Returns:
        ChatResponse containing the AI response.
    """
    conversation_id = req.conversation_id
    graph = _get_or_create_graph(conversation_id)
    
    user_message = HumanMessage(content=req.text)
    updated_state = graph.invoke({"messages": [user_message]})
    
    if graph.get_state() == END:
        logger.info(f"Graph reached END for conversation_id: {conversation_id}")
        _delete_graph(conversation_id)
        return ChatResponse(
            message=updated_state["messages"][-1].content,
            conversation_id=conversation_id,
            chat_complete=True
        )
   
    return ChatResponse(
        message=updated_state["messages"][-1].content,
        conversation_id=conversation_id,
        chat_complete=False
    )

