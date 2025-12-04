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
    """Create a sample state with transcripts, topic, and details."""
    return {
        "transcripts": [
            "This is a long transcript about AI and machine learning...",
            "Another transcript discussing neural networks...",
        ],
        "topic": "tech",
        "details": "AI and machine learning",
    }


def test_core_text_extraction_node_success(sample_state):
    """Test successful core text extraction."""
    mock_extracted_texts = [
        "Extracted core text about AI",
        "Extracted core text about neural networks",
    ]
    
    with patch("src.graph.nodes.core_text_extraction_node.extract_core_text") as mock_extract:
        # Mock extract_core_text to return different texts for each transcript
        def side_effect(transcript, topic, details):
            if "AI and machine learning" in transcript:
                return mock_extracted_texts[0]
            return mock_extracted_texts[1]
        
        mock_extract.side_effect = side_effect
        
        result = core_text_extraction_node(sample_state)
        
        # Verify extract was called for each transcript
        assert mock_extract.call_count == 2
        
        # Verify output
        assert "core_texts" in result
        assert "messages" in result
        assert len(result["core_texts"]) == 2
        assert result["core_texts"] == mock_extracted_texts
        assert "2" in result["messages"][0].content  # "Extracted core text from 2 sources"


def test_core_text_extraction_node_no_transcripts():
    """Test core text extraction with no transcripts."""
    state = {
        "transcripts": [],
        "topic": "tech",
        "details": "AI",
    }
    
    with patch("src.graph.nodes.core_text_extraction_node.extract_core_text") as mock_extract:
        result = core_text_extraction_node(state)
        
        # Should not call extract_core_text
        mock_extract.assert_not_called()
        
        assert result["core_texts"] == []
        assert "Extracted core text from 0 sources" in result["messages"][0].content


def test_core_text_extraction_node_empty_topic_details():
    """Test core text extraction with empty topic/details."""
    state = {
        "transcripts": ["Some transcript"],
        "topic": "",
        "details": "",
    }
    
    with patch("src.graph.nodes.core_text_extraction_node.extract_core_text") as mock_extract:
        mock_extract.return_value = "Extracted text"
        
        result = core_text_extraction_node(state)
        
        # Should still process transcripts
        assert len(result["core_texts"]) == 1
        # Verify extract was called with empty strings
        mock_extract.assert_called_once_with("Some transcript", "", "")

