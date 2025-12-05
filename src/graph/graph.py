from langgraph.graph import StateGraph, END
from src.graph.nodes import (
    topic_extraction_node, check_db_node, ask_date_node,
    find_url_node, core_text_extraction_node,
    relevance_rating_node, fetch_from_db_node,
    generate_contant_node
)
from src.dto.graph_dto import MessageGraph
from src.config.logger import get_logger

logger = get_logger("GraphRouting")

def build_graph() -> StateGraph:
    builder = StateGraph(state_schema=MessageGraph)

    # -----------------------
    # Nodes
    # -----------------------
    builder.add_node("TOPIC_EXTRACTION", topic_extraction_node)
    builder.add_node("CHECK_DB", check_db_node)
    builder.add_node("ASK_DATE_RELEVANT", ask_date_node)
    builder.add_node("FIND_URL", find_url_node)
    builder.add_node("CORE_TEXT", core_text_extraction_node)
    builder.add_node("RATE_RELEVANCE", relevance_rating_node)
    builder.add_node("FETCH_DB", fetch_from_db_node)
    builder.add_node("GENERATE_CONTENT", generate_contant_node)

    # Entry
    builder.set_entry_point("TOPIC_EXTRACTION")

    # Topic extraction retries
    def route_after_topic_extraction(state: MessageGraph) -> str:
        """Route after topic extraction: retry if needed, exit if failed after retries, continue if successful."""
        topic = state.get("topic", "")
        retry_count = state.get("retry_count", 0)
        
        # If topic extraction failed after retries, exit gracefully
        if not topic and retry_count >= 2:
            return END
        
        # If topic is empty and retries available, retry
        if not topic and retry_count < 2:
            return "TOPIC_EXTRACTION"
        
        # Topic extracted successfully, continue to check DB
        return "CHECK_DB"
    
    builder.add_conditional_edges(
        "TOPIC_EXTRACTION",
        route_after_topic_extraction,
        {
            "TOPIC_EXTRACTION": "TOPIC_EXTRACTION",
            "CHECK_DB": "CHECK_DB",
            END: END
        }
    )

    # Check DB
    def route_after_check_db(state: MessageGraph) -> str:
        """Route after checking DB: ask about date if topic found, find URLs if not."""
        topic_in_db = state.get("topic_in_db", False)
        logger.info(f"Routing after CHECK_DB: topic_in_db={topic_in_db}, type={type(topic_in_db)}")
        
        if topic_in_db:
            logger.info("Routing to ASK_DATE_RELEVANT")
            return "ASK_DATE_RELEVANT"
        else:
            logger.info("Routing to FIND_URL")
            return "FIND_URL"
    
    builder.add_conditional_edges(
        "CHECK_DB",
        route_after_check_db,
        {"ASK_DATE_RELEVANT": "ASK_DATE_RELEVANT", "FIND_URL": "FIND_URL"}
    )

    # Ask user if DB data date ok
    def route_after_ask_date(state: MessageGraph) -> str:
        """Route after asking about date: wait for input, fetch from DB if yes, find URLs if no."""
        user_confirmed_date = state.get("user_confirmed_date")
        logger.info(f"Routing after ASK_DATE_RELEVANT: user_confirmed_date={user_confirmed_date}")

        # If user hasn't responded yet, pause execution (graph_factory_service will detect and pause)
        if user_confirmed_date is None:
            logger.info("User hasn't responded yet, pausing at ASK_DATE_RELEVANT")
            return END  # Pause the graph - graph_factory_service will detect and handle
        
        # User responded: fetch from DB if yes, find URLs if no
        if user_confirmed_date:
            logger.info("User confirmed date, routing to FETCH_DB")
            return "FETCH_DB"
        else:
            logger.info("User rejected date, routing to FIND_URL")
            return "FIND_URL"
    
    builder.add_conditional_edges(
        "ASK_DATE_RELEVANT",
        route_after_ask_date,
        {
            "FETCH_DB": "FETCH_DB",
            "FIND_URL": "FIND_URL",
            END: END
        }
    )

    # Main content pipeline
    builder.add_edge("FIND_URL", "CORE_TEXT")
    builder.add_edge("CORE_TEXT", "RATE_RELEVANCE")
    builder.add_edge("RATE_RELEVANCE", "GENERATE_CONTENT")
    builder.add_edge("FETCH_DB", "GENERATE_CONTENT")
    builder.add_edge("GENERATE_CONTENT", END)

    # Compile graph and add interrupt after ASK_DATE to pause when waiting for user input
    graph = builder.compile()
    return graph
