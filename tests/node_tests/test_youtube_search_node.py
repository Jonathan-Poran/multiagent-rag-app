"""
Tests for YouTube search node.
"""

import pytest
from unittest.mock import patch, Mock
from langchain_core.messages import AIMessage
from src.graph.nodes.youtube_search_node import youtube_search_node
from src.graph.state import MessageGraph


@pytest.fixture
def sample_state():
    """Create a sample state with topic and details."""
    return {
        "topic": "tech",
        "details": "AI and machine learning",
        "video_urls": None,
    }


def test_youtube_search_node_success(sample_state):
    """Test successful YouTube search."""
    mock_video_urls = [
        "https://youtube.com/watch?v=video1",
        "https://youtube.com/watch?v=video2",
    ]
    
    with patch("src.graph.nodes.youtube_search_node.search_youtube_videos") as mock_search:
        mock_search.return_value = mock_video_urls
        
        result = youtube_search_node(sample_state)
        
        # Verify search was called with correct parameters
        mock_search.assert_called_once_with("tech", "AI and machine learning", max_results=5)
        
        # Verify output
        assert "video_urls" in result
        assert "messages" in result
        assert result["video_urls"] == mock_video_urls
        assert len(result["messages"]) == 1
        assert isinstance(result["messages"][0], AIMessage)
        assert "2" in result["messages"][0].content  # "Found 2 YouTube videos"


def test_youtube_search_node_no_results(sample_state):
    """Test YouTube search with no results."""
    with patch("src.graph.nodes.youtube_search_node.search_youtube_videos") as mock_search:
        mock_search.return_value = []
        
        result = youtube_search_node(sample_state)
        
        assert result["video_urls"] == []
        assert "Found 0 YouTube videos" in result["messages"][0].content


def test_youtube_search_node_empty_topic():
    """Test YouTube search with empty topic."""
    state = {"topic": "", "details": ""}
    
    with patch("src.graph.nodes.youtube_search_node.search_youtube_videos") as mock_search:
        mock_search.return_value = []
        
        result = youtube_search_node(state)
        
        mock_search.assert_called_once_with("", "", max_results=5)
        assert result["video_urls"] == []


def test_youtube_search_node_missing_fields():
    """Test YouTube search with missing topic/details."""
    state = {}
    
    with patch("src.graph.nodes.youtube_search_node.search_youtube_videos") as mock_search:
        mock_search.return_value = []
        
        result = youtube_search_node(state)
        
        # Should use empty strings as defaults
        mock_search.assert_called_once_with("", "", max_results=5)

