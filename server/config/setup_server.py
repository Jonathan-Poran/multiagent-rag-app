from dotenv import load_dotenv
load_dotenv() 

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from server.api import register_routes
from server.graph.graph import graph
from server.config.logger import logger, set_logger_level
from server.config.settings import settings

def setup_server() -> FastAPI:
    # Initialize logger with settings
    set_logger_level(settings.log_level)
    logger.info("Setting up the server...")
    logger.info(f"Port: {settings.port}")
    logger.debug(f"Log level set to: {settings.log_level}")
    
    # Check critical environment variables
    if not settings.openai_api_key:
        logger.warning("OPENAI_API_KEY is not set - graph functionality may not work")
    else:
        logger.info("OPENAI_API_KEY is configured")
    if not settings.tavily_api_key:
        logger.warning("TAVILY_API_KEY is not set - graph functionality may not work")
    else:
        logger.info("TAVILY_API_KEY is configured")
    if not settings.mongodb_uri:
        logger.warning("MONGODB_URI is not set - graph functionality may not work")
    else:
        logger.info("MONGODB_URI is configured")
    if not settings.mongodb_db_name:
        logger.warning("MONGODB_DB_NAME is not set - graph functionality may not work")
    else:
        logger.info("MONGODB_DB_NAME is configured")
    
    # Only print graph in development (not in production)
    # Wrap in try-except to prevent startup failures
    try:
        import sys
        if sys.stdout.isatty():  # Only if running in a terminal
            from server.graph.graph import print_graph
            print_graph()  # Keep print for graph visualization
    except Exception as e:
        logger.warning(f"Could not print graph visualization: {e}")

    app = FastAPI(title="Multi-Agent RAG App", version="1.0.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Serve static frontend
    static_path = os.path.join(os.path.dirname(__file__), "../../static")
    static_path = os.path.abspath(static_path)

    app.mount("/static", StaticFiles(directory=static_path), name="static")

    @app.get("/")
    async def root():
        return FileResponse(os.path.join(static_path, "index.html"))

    register_routes(app)
    return app