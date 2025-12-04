"""
Standalone script to generate a Mermaid graph PNG.
No imports from src.config or multiagent to avoid circular imports.
"""

from pathlib import Path
from langgraph.graph import StateGraph, END

# Import only nodes and constants
from src.graph.nodes import (
    topic_extraction_node,
    youtube_search_node,
    tbd_search_node,
    transcript_fetch_node,
    core_text_extraction_node,
    relevance_rating_node,
    fact_verification_node,
    linkedin_generation_node,
    instagram_tiktok_generation_node,
    output_node,
)
from src.graph.consts import (
    TOPIC_EXTRACTION,
    YOUTUBE_SEARCH,
    TBD_SEARCH,
    TRANSCRIPT_FETCH,
    CORE_TEXT_EXTRACTION,
    RELEVANCE_RATING,
    FACT_VERIFICATION,
    LINKEDIN_GENERATION,
    INSTAGRAM_TIKTOK_GENERATION,
    OUTPUT,
)
from src.graph.edges import route_after_topic_extraction, route_after_youtube_search
from src.graph.state import MessageGraph

# Output path
desktop_path = Path.home() / "Desktop" / "graph_diagram.mmd"

# --------------------------
# Build the graph locally
# --------------------------
builder = StateGraph(state_schema=MessageGraph)

# Add nodes
builder.add_node(TOPIC_EXTRACTION, topic_extraction_node)
builder.add_node(YOUTUBE_SEARCH, youtube_search_node)
builder.add_node(TBD_SEARCH, tbd_search_node)
builder.add_node(TRANSCRIPT_FETCH, transcript_fetch_node)
builder.add_node(CORE_TEXT_EXTRACTION, core_text_extraction_node)
builder.add_node(RELEVANCE_RATING, relevance_rating_node)
builder.add_node(FACT_VERIFICATION, fact_verification_node)
builder.add_node(LINKEDIN_GENERATION, linkedin_generation_node)
builder.add_node(INSTAGRAM_TIKTOK_GENERATION, instagram_tiktok_generation_node)
builder.add_node(OUTPUT, output_node)

# Entry point
builder.set_entry_point(TOPIC_EXTRACTION)

# Conditional edges
builder.add_conditional_edges(
    TOPIC_EXTRACTION,
    route_after_topic_extraction,
    {TOPIC_EXTRACTION: TOPIC_EXTRACTION, YOUTUBE_SEARCH: YOUTUBE_SEARCH}
)
builder.add_edge(YOUTUBE_SEARCH, TBD_SEARCH)
builder.add_conditional_edges(
    TBD_SEARCH,
    route_after_youtube_search,
    {TRANSCRIPT_FETCH: TRANSCRIPT_FETCH, CORE_TEXT_EXTRACTION: CORE_TEXT_EXTRACTION}
)
builder.add_edge(TRANSCRIPT_FETCH, CORE_TEXT_EXTRACTION)
builder.add_edge(CORE_TEXT_EXTRACTION, RELEVANCE_RATING)
builder.add_edge(RELEVANCE_RATING, FACT_VERIFICATION)
builder.add_edge(FACT_VERIFICATION, LINKEDIN_GENERATION)
builder.add_edge(LINKEDIN_GENERATION, INSTAGRAM_TIKTOK_GENERATION)
builder.add_edge(INSTAGRAM_TIKTOK_GENERATION, OUTPUT)
builder.add_edge(OUTPUT, END)

graph = builder.compile()
