"""
Tests for TBD search node.
"""

import pytest
from unittest.mock import patch
from langchain_core.messages import AIMessage
from src.graph.nodes.tbd_search_node import tbd_search_node
from src.graph.state import MessageGraph


@pytest.fixture
def sample_state():
    """Create a sample state with topic and details."""
    return {
        "topic": "tech",
        "details": "AI and machine learning",
    }


def test_tbd_search_node_success(sample_state):
    """Test successful TBD search."""
    mock_results = [
        {"url": "https://example.com/article1", "content": "Article 1"},
        {"url": "https://example.com/article2", "content": "Article 2"},
    ]
    
    with patch("src.graph.nodes.tbd_search_node.search_tavily") as mock_search:
        mock_search.return_value = mock_results
        
        result = tbd_search_node(sample_state)
        
        # Verify search was called
        expected_query = "tech AI and machine learning"
        mock_search.assert_called_once_with(expected_query, max_results=5)
        
        # Verify output
        assert "messages" in result
        assert len(result["messages"]) == 1
        assert isinstance(result["messages"][0], AIMessage)
        assert "2" in result["messages"][0].content  # "Found 2 additional sources"


def test_tbd_search_node_no_results(sample_state):
    """Test TBD search with no results."""
    with patch("src.graph.nodes.tbd_search_node.search_tavily") as mock_search:
        mock_search.return_value = []
        
        result = tbd_search_node(sample_state)
        
        assert "Found 0 additional sources" in result["messages"][0].content


def test_tbd_search_node_empty_state():
    """Test TBD search with empty state."""
    state = {}
    
    with patch("src.graph.nodes.tbd_search_node.search_tavily") as mock_search:
        mock_search.return_value = []
        
        result = tbd_search_node(state)
        
        # Should handle empty topic/details gracefully
        mock_search.assert_called_once()

