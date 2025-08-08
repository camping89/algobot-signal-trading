from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import uvicorn
from contextlib import asynccontextmanager
from app.discord_app.config import discord_settings

from app.discord_app.routers import messages as discord_messages
from app.discord_app.services.discord_message_service import DiscordMessageService
from app.discord_app.services.discord_scheduler import DiscordScheduler

# Create Discord service instances
discord_message_service = DiscordMessageService()
discord_scheduler = DiscordScheduler(discord_message_service)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Discord service lifespan"""
    # Startup
    try:
        await discord_message_service.initialize_db()
        await discord_scheduler.start_scheduler()
        logger.info("Discord services initialized")
    except Exception as e:
        logger.error(f"Discord startup error: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    try:
        await discord_scheduler.stop_scheduler()
        await discord_message_service.close_db_connection()
        logger.info("Discord services shut down")
    except Exception as e:
        logger.error(f"Error shutting down Discord services: {str(e)}")

app = FastAPI(
    title="Discord Bot API",
    description="Discord message collection service",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    discord_status = "running" if discord_scheduler.is_running() else "stopped"
    return {
        "status": "healthy" if discord_status == "running" else "unhealthy",
        "service": "discord-bot",
        "discord_scheduler": discord_status
    }

# Include Discord router
app.include_router(
    discord_messages.get_router(discord_message_service),
    prefix="/discord"
)

if __name__ == "__main__":
    uvicorn.run("main-discord:app", host="0.0.0.0", port=3001, reload=True)