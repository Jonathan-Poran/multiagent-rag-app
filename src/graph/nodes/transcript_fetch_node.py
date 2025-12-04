"""
Transcript fetch node - fetches transcripts for YouTube videos.
"""

from langchain_core.messages import AIMessage
from ..state import MessageGraph
from src.services.youtube_service import fetch_transcript


def transcript_fetch_node(state: MessageGraph) -> dict:
    """
    Fetch transcripts for all video URLs.
    
    Args:
        state: The current graph state with video URLs.
    
    Returns:
        dict: Updated state with transcripts.
    """
    video_urls = state.get("video_urls", [])
    transcripts = []
    
    for video_url in video_urls:
        transcript = fetch_transcript(video_url)
        if transcript:
            transcripts.append(transcript)
    
    return {
        "transcripts": transcripts,
        "messages": [AIMessage(content=f"Fetched {len(transcripts)} transcripts")]
    }

