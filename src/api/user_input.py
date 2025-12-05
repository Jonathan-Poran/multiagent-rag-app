from fastapi import APIRouter
from src.dto import ChatResponse, UserMessage
from src.services.graph_factory_service import route_input_to_graph
from src.config.logger import get_logger

router = APIRouter()
logger = get_logger("FastAPI_Server")


@router.post("", response_model=ChatResponse)
async def user_input(req: UserMessage):
    """
    Handle user chat message in a conversation.
    
    Args:
        req: Chat request with message text and conversation_id.
    
    Returns:
        ChatResponse: Response with AI message text and conversation_id.
    """
    logger.info(f"Received chat for conversation {req.conversation_id}")
    try:
        return route_input_to_graph(req)
    except Exception as e:
        logger.error(f"Error processing chat: {e}", exc_info=True)
        raise
