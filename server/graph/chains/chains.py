from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from server.config.settings import settings

generation_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a highly experienced chef. I will tell you what ingredients are in the fridge, 
            and you will provide a simple, clear dish description followed by an easy recipe that can be made using only those ingredients."""
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

generation_chain = generation_prompt | llm
reflection_chain = reflection_prompt | llm
