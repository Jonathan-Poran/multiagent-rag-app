
import os
from dotenv import load_dotenv
load_dotenv()

from langchain_core.messages import HumanMessage
from pymongo import MongoClient, errors

from graph.graph import graph

try:
    client = MongoClient(os.getenv("MONGODB_URI"))
    db = client[os.getenv("MONGODB_DB_NAME")]
    collection = db["inputs"]
    print("Successfully connected to MongoDB")
except errors.ConnectionError as e:
    print("Failed to connect to MongoDB:", e)
    collection = None  # prevent further insertions





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

