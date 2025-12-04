"""
Chat-related DTOs for user input and AI responses.
"""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request DTO for user chat messages."""
    
    text: str = Field(
        ...,
        description="The user's message text",
        min_length=1,
        max_length=5000,
        examples=["I want to create content about AI and machine learning"]
    )
    conversation_id: str = Field(
        ...,
        description="Unique identifier for the conversation",
        min_length=1,
        examples=["507f1f77bcf86cd799439011"]
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "I want to create content about AI and machine learning",
                "conversation_id": "507f1f77bcf86cd799439011"
            }
        }


class ChatResponse(BaseModel):
    """Response DTO for AI chat messages."""
    
    message: str = Field(
        ...,
        description="The AI's response message",
        examples=["I'll help you create content about AI and machine learning. Let me search for the latest information..."]
    )
    conversation_id: str = Field(
        ...,
        description="The conversation ID this response belongs to",
        examples=["507f1f77bcf86cd799439011"]
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "I'll help you create content about AI and machine learning. Let me search for the latest information...",
                "conversation_id": "507f1f77bcf86cd799439011"
            }
        }

