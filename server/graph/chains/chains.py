from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from server.config.settings import settings


class ContentStructure(BaseModel):
    """Structure for organizing social media content requests."""
    topic: str = Field(description="General topic category (e.g., fashion, sports, tech, food, travel, health, entertainment, business, education)")
    details: str = Field(description="Specific sub-topic or detailed content description (e.g., 'football, european league' for sports, 'new langgraph tools' for tech)")


generation_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a social media content organizer. Your task is to analyze user messages about what content they want to create for social media and extract:
            1. The general topic (e.g., fashion, sports, tech, food, travel, health, entertainment, business, education)
            2. The specific details or sub-topics (e.g., for sports: "football, european league", for tech: "new langgraph tools")

            Return a JSON structure with "topic" and "details" fields. Be specific and accurate in categorizing the user's request."""
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

reflection_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a highly experienced chef. You will be given a dish description and its recipe. 
            Your task is to choose a better dish,
            you need to describe the new dish and recipe
            and also list the missing ingredients that arent in the ingredients list."""
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

llm = ChatOpenAI(api_key=settings.openai_api_key)
llm_structured = ChatOpenAI(api_key=settings.openai_api_key).with_structured_output(ContentStructure)

generation_chain = generation_prompt | llm_structured
reflection_chain = reflection_prompt | llm
