from datetime import datetime
from src.dto.graph_dto import MessageGraph
from langchain_core.messages import AIMessage, HumanMessage
from src.config.logger import get_logger

logger = get_logger("AskDateNode")

def ask_date_node(state: MessageGraph) -> dict:
    """
    Ask user if the date of existing DB data is acceptable.
    Sets 'user_confirmed_date' = True/False based on user input.
    Pauses for input if needed.
    """
    db_content = state.get("db_content", "")
    if not db_content:
        # fallback, should not happen
        return {"user_confirmed_date": False}

    # Check if we already have user input (user has responded)
    user_confirmed_date = state.get("user_confirmed_date")
    if user_confirmed_date is not None:
        # User has already responded, return the confirmation
        return {"user_confirmed_date": user_confirmed_date}
    
    # Check the latest message to see if user has responded
    latest_message = None
    for msg in reversed(state.get("messages", [])):
        if isinstance(msg, HumanMessage):
            latest_message = msg.content.lower().strip()
            break
    
    # If user has responded, parse yes/no
    if latest_message:
        if latest_message in ["yes", "y", "ok", "okay", "sure", "fine"]:
            return {"user_confirmed_date": True}
        elif latest_message in ["no", "n", "nope"]:
            return {"user_confirmed_date": False}
    
    # No response yet, ask the question
    topic = state.get("topic", "")
    date = state.get("date", "")
    
    # Format date to DD/MM/YYYY format
    formatted_date = ""
    if date:
        try:
            # Handle datetime object
            if isinstance(date, datetime):
                formatted_date = date.strftime("%d/%m/%Y")
            # Handle string date (if it's already a string)
            elif isinstance(date, str):
                # Try to parse and reformat if it's a datetime string
                try:
                    parsed_date = datetime.fromisoformat(date.replace('Z', '+00:00'))
                    formatted_date = parsed_date.strftime("%d/%m/%Y")
                except (ValueError, AttributeError):
                    # If parsing fails, use as-is or try other formats
                    formatted_date = date
        except Exception as e:
            logger.warning(f"Failed to format date: {e}, using original value")
            formatted_date = str(date) if date else ""
    
    logger.info(f"ASK_DATE_RELEVANT node executing: topic={topic}, date={date}, formatted_date={formatted_date}, db_content length={len(db_content)}")
    msg = AIMessage(content=f"I have existing data for '{topic}' from {formatted_date}. Is this date okay for you? (yes/no)")
    logger.info("Returning message to ask user about date")
    return {"messages": [msg]}  # This will pause for user input via graph routing
