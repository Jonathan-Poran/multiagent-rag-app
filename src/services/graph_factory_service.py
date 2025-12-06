from typing import Optional
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage
from src.dto.chat_dto import UserMessage, ChatResponse
from src.dto.graph_dto import MessageGraph
from src.config.logger import get_logger
from src.graph.graph import build_graph

logger = get_logger("GraphFactory")

# Global registry: conversation_id -> graph instance
_graph_registry: dict[str, StateGraph] = {}
# State registry: conversation_id -> last state
_state_registry: dict[str, MessageGraph] = {}

# -----------------------
# Factory helpers
# -----------------------

def _get_or_create_graph(conversation_id: str) -> StateGraph:
    if conversation_id not in _graph_registry:
        _graph_registry[conversation_id] = build_graph()
        logger.info(f"Created new graph for conversation_id={conversation_id}")
    return _graph_registry[conversation_id]

def _delete_graph(conversation_id: str):
    if conversation_id in _graph_registry:
        del _graph_registry[conversation_id]
        logger.info(f"Deleted graph for conversation_id={conversation_id}")
    if conversation_id in _state_registry:
        del _state_registry[conversation_id]
        logger.info(f"Deleted state for conversation_id={conversation_id}")

def _get_graph(conversation_id: str) -> Optional[StateGraph]:
    return _graph_registry.get(conversation_id)

# -----------------------
# Route user input
# -----------------------

def route_input_to_graph(req: UserMessage) -> ChatResponse:
    """
    Send user message to graph and handle multi-turn logic.
    Graph decides next step and END detection.
    """
    conversation_id = req.conversation_id
    graph = _get_or_create_graph(conversation_id)

    # Wrap user input in LangChain message
    user_message = HumanMessage(content=req.text)

    # Get previous state if it exists (for continuing from pause)
    previous_state = _state_registry.get(conversation_id)
    
    if previous_state:
        # Merge new message with previous state
        logger.info(f"Continuing from previous state for conversation_id={conversation_id}")
        # Add the new user message to existing messages
        existing_messages = previous_state.get("messages", [])
        existing_messages.append(user_message)
        # Create new state with updated messages and all previous state
        input_state = {**previous_state, "messages": existing_messages}
        # Clear the stored state since we're continuing
        del _state_registry[conversation_id]
    else:
        # Start fresh with just the new message
        input_state = {"messages": [user_message]}

    # Invoke the graph
    updated_state = graph.invoke(input_state)

    # Determine what the graph wants to do next
    next_step = updated_state.get("_next")
    
    # If user_confirmed_date is None, we're waiting for yes/no response
    user_confirmed_date = updated_state.get("user_confirmed_date")
    topic_in_db = updated_state.get("topic_in_db", False)
    awaiting_date_confirmation = topic_in_db and user_confirmed_date is None

    # Check if graph ended but we're waiting for user input (ASK_DATE_RELEVANT pause)
    if next_step is None and awaiting_date_confirmation:
        # Graph paused at ASK_DATE_RELEVANT, waiting for user response
        logger.info(f"Graph paused at ASK_DATE_RELEVANT, waiting for user input for conversation_id={conversation_id}")
        # Store the state so we can continue from here when user responds
        _state_registry[conversation_id] = updated_state
        last_message = updated_state["messages"][-1].content if updated_state.get("messages") else "Waiting for your response..."
        return ChatResponse(
            message=last_message,
            conversation_id=conversation_id,
            chat_complete=False,
            awaiting_user_input=True
        )

    if next_step is None:
        # Graph finished
        logger.info(f"Graph reached END for conversation_id={conversation_id}")
        _delete_graph(conversation_id)
        return ChatResponse(
            message=updated_state["messages"][-1].content,
            conversation_id=conversation_id,
            chat_complete=True
        )

    elif next_step == "__await_input__" or awaiting_date_confirmation:
        # Graph is paused, waiting for more user input
        return ChatResponse(
            message=updated_state["messages"][-1].content,
            conversation_id=conversation_id,
            chat_complete=False,
            awaiting_user_input=True
        )

    else:
        # Graph will continue automatically
        return ChatResponse(
            message=updated_state["messages"][-1].content,
            conversation_id=conversation_id,
            chat_complete=False
        )
