from dotenv import load_dotenv
load_dotenv()  # Load environment variables before importing modules that need them

from fastapi import FastAPI
from server.api import register_routes
from server.graph.graph import graph, print_graph

def setup_server() -> FastAPI:
    print("Setting up the server...")
    print_graph()

    app = FastAPI()
    register_routes(app)
    return app

