from dotenv import load_dotenv
load_dotenv() 

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from fastapi import FastAPI
from server.api import register_routes
from server.graph.graph import graph, print_graph
from server.config.logger import logger, set_logger_level
from server.config.settings import settings

def setup_server() -> FastAPI:
    # Initialize logger with settings
    set_logger_level(settings.log_level)
    logger.info("Setting up the server...")
    logger.debug(f"Log level set to: {settings.log_level}")
    
    print_graph()  # Keep print for graph visualization

    app = FastAPI()

    # Serve static frontend
    static_path = os.path.join(os.path.dirname(__file__), "../../static")
    static_path = os.path.abspath(static_path)

    app.mount("/static", StaticFiles(directory=static_path), name="static")

    @app.get("/")
    async def root():
        return FileResponse(os.path.join(static_path, "index.html"))

    register_routes(app)
    return app