
import os
from dotenv import load_dotenv
load_dotenv()

from typing import  TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import StateGraph, END, add_messages

from chains import generation_chain, reflection_chain

class MessageGraph(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


REFLECT="reflect"
GENERATE="generate"
from pymongo import MongoClient, errors

try:
    client = MongoClient(os.getenv("MONGODB_URI"))
    db = client[os.getenv("MONGODB_DB_NAME")]
    collection = db["inputs"]
    print("Successfully connected to MongoDB")
except errors.ConnectionError as e:
    print("Failed to connect to MongoDB:", e)
    collection = None  # prevent further insertions


def generation_node(state: MessageGraph):
    result = generation_chain.invoke({"messages": state["messages"]})
    return {"messages": [result]}


def reflection_node(state: MessageGraph):
    result = reflection_chain.invoke({"messages": state["messages"]})
    return {"messages": [HumanMessage(result.content)]} #this message annotated as HumanMessage because its simulates the user's response to the reflection

def should_continue(state: MessageGraph) -> str:
    print(state["messages"][-1].content)
    print("\nAre you happy with the recipe? (y/n)")
    return END if input() == "y" else REFLECT

builder = StateGraph(state_schema=MessageGraph)

builder.add_node(GENERATE, generation_node)
builder.set_entry_point(GENERATE)

builder.add_node(REFLECT, reflection_node)

builder.add_conditional_edges(GENERATE, should_continue,path_map={END: END, REFLECT: REFLECT})
builder.add_conditional_edges(REFLECT, should_continue,path_map={END: END, REFLECT: REFLECT})

graph = builder.compile()





if __name__ == "__main__":
    # Draw the graph in mermaid format for visualization
    print(graph.get_graph().draw_mermaid())
    
    
    print("\n\nStarting the application...\n")
    print("Please enter the ingredients you have in the fridge:")
    # eggs, tomatoes, garlic and basil
    input_message = HumanMessage(content="I have some "+input()+ " in the fridge.")
    if collection is not None:
        try:
            collection.insert_one({"input": input_message.content})
        except errors.PyMongoError as e:
            print("Failed to insert document into MongoDB:", e)
    else:
        print("Skipping MongoDB insertion due to connection issues.")
    print()

    response = graph.invoke({"messages": [input_message]})
    print("bon appetit!")

