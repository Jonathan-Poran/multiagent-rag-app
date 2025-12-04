"""
Tests for transcript fetch node.
"""

import pytest
from unittest.mock import patch
from langchain_core.messages import AIMessage
from src.graph.nodes.transcript_fetch_node import transcript_fetch_node
from src.graph.state import MessageGraph


@pytest.fixture
def sample_state():
    """Create a sample state with video URLs."""
    return {
        "video_urls": [
            "https://youtube.com/watch?v=video1",
            "https://youtube.com/watch?v=video2",
        ],
        "transcripts": None,
    }


def test_transcript_fetch_node_success(sample_state):
    """Test successful transcript fetching."""
    mock_transcripts = [
        "This is the transcript for video 1",
        "This is the transcript for video 2",
    ]
    
    with patch("src.graph.nodes.transcript_fetch_node.fetch_transcript") as mock_fetch:
        # Mock fetch_transcript to return different transcripts for each URL
        def side_effect(url):
            if "video1" in url:
                return mock_transcripts[0]
            elif "video2" in url:
                return mock_transcripts[1]
            return None
        
        mock_fetch.side_effect = side_effect
        
        result = transcript_fetch_node(sample_state)
        
        # Verify fetch was called for each URL
        assert mock_fetch.call_count == 2
        
        # Verify output
        assert "transcripts" in result
        assert "messages" in result
        assert len(result["transcripts"]) == 2
        assert result["transcripts"] == mock_transcripts
        assert "2" in result["messages"][0].content  # "Fetched 2 transcripts"


def test_transcript_fetch_node_no_videos():
    """Test transcript fetch with no video URLs."""
    state = {"video_urls": []}
    
    with patch("src.graph.nodes.transcript_fetch_node.fetch_transcript") as mock_fetch:
        result = transcript_fetch_node(state)
        
        # Should not call fetch_transcript
        mock_fetch.assert_not_called()
        
        assert result["transcripts"] == []
        assert "Fetched 0 transcripts" in result["messages"][0].content


def test_transcript_fetch_node_some_failures(sample_state):
    """Test transcript fetch when some videos fail."""
    with patch("src.graph.nodes.transcript_fetch_node.fetch_transcript") as mock_fetch:
        # First succeeds, second fails
        def side_effect(url):
            if "video1" in url:
                return "Transcript 1"
            return None  # video2 fails
        
        mock_fetch.side_effect = side_effect
        
        result = transcript_fetch_node(sample_state)
        
        # Should only include successful transcripts
        assert len(result["transcripts"]) == 1
        assert result["transcripts"][0] == "Transcript 1"
        assert "Fetched 1 transcripts" in result["messages"][0].content


def test_transcript_fetch_node_missing_video_urls():
    """Test transcript fetch with missing video_urls field."""
    state = {}
    
    with patch("src.graph.nodes.transcript_fetch_node.fetch_transcript") as mock_fetch:
        result = transcript_fetch_node(state)
        
        # Should handle missing field gracefully
        assert result["transcripts"] == []

