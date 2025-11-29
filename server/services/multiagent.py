from langchain_core.messages import HumanMessage
from fastapi import HTTPException
from server.services.mongo import get_collection
from server.graph.graph import graph


def run_graph(text: str):
    input_message = HumanMessage(content=text)
    return (graph.invoke({"messages": [input_message]}).get("messages")[-1].content)


async def process_user_input_food(request: str):
    collection = get_collection()

    user_text = f"I have some {request} in the fridge."

    # Save to DB
    try:
        if collection is not None:
            collection.insert_one({"input": user_text})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MongoDB insertion failed: {e}")

    # Run the graph
    try:
        result = run_graph(user_text)
        return {"response": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Graph error: {e}")
