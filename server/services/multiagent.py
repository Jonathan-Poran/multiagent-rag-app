from langchain_core.messages import HumanMessage
from fastapi import HTTPException
from server.services.mongo import get_collection
from server.graph.graph import graph
from server.config.logger import get_logger

logger = get_logger("multiagent")


def run_graph(text: str):
    logger.info("Running graph with user input")
    logger.debug(f"Input text: {text[:100]}...")  # Log first 100 chars
    input_message = HumanMessage(content=text)
    result = graph.invoke({"messages": [input_message]}).get("messages")[-1].content
    logger.info("Graph execution completed successfully")
    return result


async def process_user_input_food(request: str):
    logger.info(f"Processing user input food request: {request[:50]}...")
    collection = get_collection()

    user_text = f"I have some {request} in the fridge."

    # Save to DB
    try:
        if collection is not None:
            collection.insert_one({"input": user_text})
            logger.info("User input saved to MongoDB")
        else:
            logger.warning("MongoDB collection not available, skipping save")
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
