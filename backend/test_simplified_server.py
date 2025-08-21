from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from dotenv import load_dotenv
from utils.config import config, EnvMode
import asyncio
from utils.logger import logger
import sys

load_dotenv()

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

instance_id = "single"

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting up FastAPI application with instance ID: {instance_id} in {config.ENV_MODE.value} mode")
    try:
        # Minimal initialization - just log that we're starting
        logger.info("Minimal lifespan initialization complete")
        
        yield
        
        # Minimal cleanup
        logger.info("Minimal lifespan cleanup complete")
    except Exception as e:
        logger.error(f"Error during application startup: {e}")
        raise

app = FastAPI(lifespan=lifespan)

# Define allowed origins based on environment
allowed_origins = ["https://www.suna.so", "https://suna.so", "http://localhost:3000"]
allow_origin_regex = None

# Add staging-specific origins
if config.ENV_MODE == EnvMode.STAGING:
    allowed_origins.append("https://staging.suna.so")
    allow_origin_regex = r"https://suna-.*-prjcts\.vercel\.app"

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=allow_origin_regex,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Project-Id"],
)

@app.get("/api/health")
async def health_check():
    """Health check endpoint to verify API is working."""
    logger.info("Health check endpoint called")
    return {
        "status": "ok", 
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "instance_id": instance_id
    }

@app.post("/api/agent/initiate")
async def test_agent_initiate():
    """Test endpoint for agent initiation with sandbox bypass."""
    logger.info("Agent initiate endpoint called - using bypass mode")
    return {
        "status": "success", 
        "message": "Sandbox bypass working in simplified server",
        "sandbox_id": "bypass-mode",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    logger.info("Starting simplified server on 0.0.0.0:8000")
    uvicorn.run(
        "test_simplified_server:app", 
        host="0.0.0.0", 
        port=8000,
        reload=False
    )