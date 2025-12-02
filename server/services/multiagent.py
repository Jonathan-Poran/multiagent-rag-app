from langchain_core.messages import HumanMessage
from fastapi import HTTPException
from server.services.mongo import save_user_input
from server.graph.graph import graph
from server.config.logger import get_logger

logger = get_logger("Multiagent")


def run_graph(text: str):
    if graph is None:
        raise HTTPException(
            status_code=503, 
            detail="Graph is not initialized. Please check server logs and configuration."
        )
    logger.info("Running graph with user input")
    logger.debug(f"Input text: {text[:100]}...")  # Log first 100 chars
    input_message = HumanMessage(content=text)
    result = graph.invoke({"messages": [input_message]}).get("messages")[-1].content
    logger.info("Graph execution completed successfully")
    return result


async def process_user_input_food(request: str):
    logger.info(f"Processing request with ingredients:\n {request}\n")

    user_text = f"I have some {request} in the fridge."

    # Save to DB
    try:
        save_user_input(user_text)
    except Exception as e:
        logger.error(f"MongoDB insertion failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"MongoDB insertion failed: {e}")

    # Run the graph
    try:
        result = run_graph(user_text)
        logger.info("Successfully processed user input")
        return {"response": result}
    except Exception as e:
        logger.error(f"Graph error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Graph error: {e}")
