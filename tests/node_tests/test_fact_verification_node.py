"""
Tests for fact verification node.
"""

import pytest
from unittest.mock import patch
from langchain_core.messages import AIMessage
from src.graph.nodes.fact_verification_node import fact_verification_node
from src.graph.state import MessageGraph


@pytest.fixture
def sample_state():
    """Create a sample state with core texts, topic, and details."""
    return {
        "core_texts": [
            "This is a verified fact about AI",
            "This is unverified information",
        ],
        "topic": "tech",
        "details": "AI and machine learning",
        "verified_texts": None,
    }


def test_fact_verification_node_success(sample_state):
    """Test successful fact verification."""
    mock_verification_results = [
        {"verified": True, "confidence": 0.9, "sources": ["source1"]},
        {"verified": False, "confidence": 0.2, "sources": []},
    ]
    
    with patch("src.graph.nodes.fact_verification_node.verify_facts") as mock_verify:
        # Mock verify_facts to return different results
        def side_effect(text, topic, details):
            if "verified fact" in text:
                return mock_verification_results[0]
            return mock_verification_results[1]
        
        mock_verify.side_effect = side_effect
        
        result = fact_verification_node(sample_state)
        
        # Verify verify_facts was called for each core text
        assert mock_verify.call_count == 2
        
        # Verify output - only verified texts should be included
        assert "verified_texts" in result
        assert "messages" in result
        assert len(result["verified_texts"]) == 1
        assert result["verified_texts"][0] == "This is a verified fact about AI"
        assert "Verified 1 texts" in result["messages"][0].content


def test_fact_verification_node_all_verified(sample_state):
    """Test fact verification when all texts are verified."""
    with patch("src.graph.nodes.fact_verification_node.verify_facts") as mock_verify:
        mock_verify.return_value = {"verified": True, "confidence": 0.9, "sources": ["source1"]}
        
        result = fact_verification_node(sample_state)
        
        # All texts should be included
        assert len(result["verified_texts"]) == 2
        assert "Verified 2 texts" in result["messages"][0].content


def test_fact_verification_node_none_verified(sample_state):
    """Test fact verification when no texts are verified."""
    with patch("src.graph.nodes.fact_verification_node.verify_facts") as mock_verify:
        mock_verify.return_value = {"verified": False, "confidence": 0.1, "sources": []}
        
        result = fact_verification_node(sample_state)
        
        # No texts should be included
        assert len(result["verified_texts"]) == 0
        assert "Verified 0 texts" in result["messages"][0].content


def test_fact_verification_node_no_core_texts():
    """Test fact verification with no core texts."""
    state = {
        "core_texts": [],
        "topic": "tech",
        "details": "AI",
    }
    
    with patch("src.graph.nodes.fact_verification_node.verify_facts") as mock_verify:
        result = fact_verification_node(state)
        
        # Should not call verify_facts
        mock_verify.assert_not_called()
        
        assert result["verified_texts"] == []

