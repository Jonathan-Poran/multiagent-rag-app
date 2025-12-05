from langgraph.graph import StateGraph, END
from src.graph.nodes import topic_extraction_node, find_url_node, check_recent_urls_node, core_text_extraction_node, generate_contant_node
from src.graph.consts import TOPIC_EXTRACTION, FIND_URL, CHECK_RECENT_URLS, CORE_TEXT_EXTRACTION, CONTENT_GENERATION
from src.graph.edges import route_after_topic_extraction
from src.graph.state import MessageGraph

def build_graph() -> StateGraph:
    """
    Build and compile a LangGraph instance.
    Graph decides when to wait for user input and when to auto-continue.
    """
    builder = StateGraph(state_schema=MessageGraph)

    # -----------------------
    # Add nodes
    # -----------------------
    builder.add_node(TOPIC_EXTRACTION, topic_extraction_node)
    builder.add_node(FIND_URL, find_url_node)
    builder.add_node(CHECK_RECENT_URLS, check_recent_urls_node)
    builder.add_node(CORE_TEXT_EXTRACTION, core_text_extraction_node)
    builder.add_node(CONTENT_GENERATION, generate_contant_node)

    # Example of a future node that waits for user input
    # builder.add_node(USER_CHOICE_NODE, user_choice_node)

    # -----------------------
    # Entry point
    # -----------------------
    builder.set_entry_point(TOPIC_EXTRACTION)

    # -----------------------
    # Conditional edges
    # -----------------------
    builder.add_conditional_edges(
        TOPIC_EXTRACTION,
        route_after_topic_extraction,
        {TOPIC_EXTRACTION: TOPIC_EXTRACTION, FIND_URL: FIND_URL}
    )

    # After find_url_node, go to core_text_extraction_node
    builder.add_edge(FIND_URL, CORE_TEXT_EXTRACTION)
    
    # After core_text_extraction_node, generate both LinkedIn and Instagram/TikTok content
    builder.add_edge(CORE_TEXT_EXTRACTION, CONTENT_GENERATION)
    
    # After content generation, end the graph
    builder.add_edge(CONTENT_GENERATION, END)

    # -----------------------
    # Compile and return
    # -----------------------
    graph = builder.compile()
    return graph
