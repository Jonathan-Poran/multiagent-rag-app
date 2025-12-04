"""
Tests for relevance rating node.
"""

import pytest
from unittest.mock import patch, Mock
from langchain_core.messages import HumanMessage, AIMessage
from src.graph.nodes.relevance_rating_node import relevance_rating_node
from src.graph.state import MessageGraph


@pytest.fixture
def sample_state():
    """Create a sample state with core texts and user message."""
    return {
        "messages": [
            HumanMessage(content="I want to create content about AI and machine learning"),
            AIMessage(content="Some AI message"),
        ],
        "core_texts": [
            "This is a text about AI and machine learning",
            "This is a text about cooking recipes",
        ],
        "relevance_scores": None,
    }


@pytest.fixture
def mock_relevance_result():
    """Mock result from relevance rating chain."""
    def create_mock(score):
        mock = Mock()
        mock.relevance_score = score
        mock.explanation = f"Relevance score: {score}"
        return mock
    return create_mock


def test_relevance_rating_node_success(sample_state, mock_relevance_result):
    """Test successful relevance rating."""
    with patch("src.graph.nodes.relevance_rating_node.relevance_rating_chain") as mock_chain:
        # Mock different scores for each text
        mock_chain.invoke.side_effect = [
            mock_relevance_result(0.9),  # High relevance
            mock_relevance_result(0.3),  # Low relevance
        ]
        
        result = relevance_rating_node(sample_state)
        
        # Verify chain was called for each core text
        assert mock_chain.invoke.call_count == 2
        
        # Verify output
        assert "relevance_scores" in result
        assert "messages" in result
        assert len(result["relevance_scores"]) == 2
        assert result["relevance_scores"] == [0.9, 0.3]
        assert "2" in result["messages"][0].content  # "Rated relevance for 2 texts"


def test_relevance_rating_node_no_core_texts():
    """Test relevance rating with no core texts."""
    state = {
        "messages": [HumanMessage(content="User request")],
        "core_texts": [],
    }
    
    with patch("src.graph.nodes.relevance_rating_node.relevance_rating_chain") as mock_chain:
        result = relevance_rating_node(state)
        
        # Should not call chain
        mock_chain.invoke.assert_not_called()
        
        assert result["relevance_scores"] == []
        assert "Rated relevance for 0 texts" in result["messages"][0].content


def test_relevance_rating_node_finds_human_message(sample_state, mock_relevance_result):
    """Test that relevance rating correctly finds HumanMessage."""
    with patch("src.graph.nodes.relevance_rating_node.relevance_rating_chain") as mock_chain:
        mock_chain.invoke.return_value = mock_relevance_result(0.8)
        
        result = relevance_rating_node(sample_state)
        
        # Verify it used the HumanMessage content, not AIMessage
        calls = mock_chain.invoke.call_args_list
        for call in calls:
            assert call[0][0]["user_request"] == "I want to create content about AI and machine learning"


def test_relevance_rating_node_no_human_message():
    """Test relevance rating when no HumanMessage exists."""
    state = {
        "messages": [AIMessage(content="Only AI messages")],
        "core_texts": ["Some text"],
    }
    
    with patch("src.graph.nodes.relevance_rating_node.relevance_rating_chain") as mock_chain:
        mock_result = Mock()
        mock_result.relevance_score = 0.5
        mock_chain.invoke.return_value = mock_result
        
        result = relevance_rating_node(state)
        
        # Should still work with empty user_message
        assert len(result["relevance_scores"]) == 1
        # Verify it was called with empty string
        assert mock_chain.invoke.call_args[0][0]["user_request"] == ""

