"""
Tests for core text extraction node.
"""

import pytest
from unittest.mock import patch
from langchain_core.messages import AIMessage
from src.graph.nodes.core_text_extraction_node import core_text_extraction_node
from src.graph.state import MessageGraph


@pytest.fixture
def sample_state():
    """Create a sample state with URLs, topic, and details."""
    return {
        "urls": [
            "https://example.com/article1",
            "https://example.com/article2",
        ],
        "topic": "tech",
        "details": "AI and machine learning",
    }


def test_core_text_extraction_node_success(sample_state):
    """Test successful core text extraction."""
    mock_extracted_text = "Extracted core text about AI and machine learning from URLs"
    
    with patch("src.graph.nodes.core_text_extraction_node.extract_core_text_from_urls") as mock_extract:
        mock_extract.return_value = mock_extracted_text
        
        result = core_text_extraction_node(sample_state)
        
        # Verify extract was called with URLs, topic, and details
        mock_extract.assert_called_once_with(
            sample_state["urls"],
            sample_state["topic"],
            sample_state["details"]
        )
        
        # Verify output
        assert "core_texts" in result
        assert len(result["core_texts"]) == 1
        assert result["core_texts"][0] == mock_extracted_text
        assert result["urls"] == sample_state["urls"]
        assert result["topic"] == sample_state["topic"]
        assert result["details"] == sample_state["details"]


def test_core_text_extraction_node_no_urls():
    """Test core text extraction with no URLs."""
    state = {
        "urls": [],
        "topic": "tech",
        "details": "AI",
    }
    
    with patch("src.graph.nodes.core_text_extraction_node.extract_core_text_from_urls") as mock_extract:
        result = core_text_extraction_node(state)
        
        # Should not call extract_core_text_from_urls
        mock_extract.assert_not_called()
        
        assert result["core_texts"] == []


def test_core_text_extraction_node_empty_topic_details():
    """Test core text extraction with empty topic/details."""
    state = {
        "urls": ["https://example.com/article"],
        "topic": "",
        "details": "",
    }
    
    with patch("src.graph.nodes.core_text_extraction_node.extract_core_text_from_urls") as mock_extract:
        mock_extract.return_value = "Extracted text"
        
        result = core_text_extraction_node(state)
        
        # Should still process URLs
        assert len(result["core_texts"]) == 1
        # Verify extract was called with empty strings for topic/details
        mock_extract.assert_called_once_with(["https://example.com/article"], "", "")

