from typing import TypedDict, Annotated, Optional
from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages


class MessageGraph(TypedDict):
    """State schema for the content generation workflow."""
    messages: Annotated[list[BaseMessage], add_messages]
    topic: Optional[str]
    details: Optional[str]
    urls: Optional[list[str]]
    video_urls: Optional[list[str]]
    tavily_urls: Optional[list[str]]
    reddit_urls: Optional[list[str]]
    transcripts: Optional[list[str]]
    core_texts: Optional[list[str]]
    relevance_scores: Optional[list[float]]
    verified_texts: Optional[list[str]]
    generated_content: Optional[dict[str, str]]

