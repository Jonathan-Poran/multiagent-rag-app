from typing import Optional
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage
from src.dto.chat_dto import UserMessage, ChatResponse
from src.config.logger import get_logger
from src.graph.graph import build_graph

logger = get_logger("GraphFactory")

# Global registry: conversation_id -> graph instance
_graph_registry: dict[str, StateGraph] = {}

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

def _get_graph(conversation_id: str) -> Optional[StateGraph]:
    return _graph_registry.get(conversation_id)

# -----------------------
# Route user input
# -----------------------

def routeInputToGraph(req: UserMessage) -> ChatResponse:
    """
    Send user message to graph and handle multi-turn logic.
    Graph decides next step and END detection.
    """
    conversation_id = req.conversation_id
    graph = _get_or_create_graph(conversation_id)

    # Wrap user input in LangChain message
    user_message = HumanMessage(content=req.text)

    # Invoke the graph
    updated_state = graph.invoke({"messages": [user_message]})

    # Determine what the graph wants to do next
    next_step = updated_state.get("_next")

    if next_step is None:
        # Graph finished
        logger.info(f"Graph reached END for conversation_id={conversation_id}")
        _delete_graph(conversation_id)
        return ChatResponse(
            message=updated_state["messages"][-1].content,
            conversation_id=conversation_id,
            chat_complete=True
        )

    elif next_step == "__await_input__":
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
