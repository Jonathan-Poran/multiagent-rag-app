from fastapi import HTTPException
from src.services.mongo_service import save_user_input
from src.services.conversation_service import add_user_message, update_conversation_state
from src.graph.graph import graph
from src.config.logger import get_logger

logger = get_logger("Multiagent")


def run_graph_with_state(conversation_state):
    """
    Run the graph with existing conversation state.
    
    Args:
        conversation_state: The current conversation state with messages.
    
    Returns:
        tuple: (AI response text, updated state)
    """
    if graph is None:
        raise HTTPException(
            status_code=503, 
            detail="Graph is not initialized. Please check server logs and configuration."
        )
    
    logger.info(f"Running graph with {len(conversation_state['messages'])} messages in state")
    
    # Invoke graph with the conversation state
    updated_state = graph.invoke(conversation_state)
    
    # Get the last message (AI response)
    if updated_state["messages"]:
        last_message = updated_state["messages"][-1]
        # Extract content from the message
        if hasattr(last_message, 'content'):
            ai_response = last_message.content
        else:
            ai_response = str(last_message)
        logger.info("Graph execution completed successfully")
        return ai_response, updated_state
    else:
        raise HTTPException(status_code=500, detail="Graph returned no messages")


async def process_user_input(request: str, conversation_id: str):
    """
    Process user input in a chat conversation.
    
    Args:
        request: The user's message text.
        conversation_id: Unique identifier for the conversation.
    
    Returns:
        dict: Response with AI message text.
    """
    logger.info(f"Processing user input for conversation {conversation_id}:\n {request}\n")

    # Save to DB
    save_user_input(request)

    # Add user message to conversation state
    conversation_state = add_user_message(conversation_id, request)

    # Run the graph with conversation state
    try:
        ai_response, updated_state = run_graph_with_state(conversation_state)
        
        # Update conversation state with graph output
        update_conversation_state(conversation_id, updated_state)
        
        logger.info("Successfully processed user input")
        return {
            "message": ai_response,
            "conversation_id": conversation_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Graph error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Graph error: {e}")
