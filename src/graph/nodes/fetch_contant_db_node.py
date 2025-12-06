from langchain_core.messages import AIMessage
from src.dto.graph_dto import MessageGraph

def fetch_from_db_node(state: MessageGraph) -> dict:
    """
    Load content from DB into core_texts for content generation.
    """
    db_content = state.get("db_content", "")
    if not db_content:
        return {"core_texts": [], "messages": [AIMessage(content="No content found in DB.")]}
    state["core_texts"] = [db_content]
    
    return {"core_texts": [db_content], "messages": [AIMessage(content="Fetched content from DB.")]}
