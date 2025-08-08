from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
import logging
from app.discord_app.models.message import DiscordFetchRequest, DiscordData
from app.discord_app.services.discord_message_service import DiscordMessageService


def get_router(discord_service: DiscordMessageService) -> APIRouter:
    router = APIRouter(tags=["Discord Messages"])
    logger = logging.getLogger(__name__)

    @router.post("/messages/fetch",
                 response_model=DiscordData,
                 summary="Fetch Discord messages",
                 description="Fetch messages from Discord channel and save to database")
    async def fetch_discord_messages(request: DiscordFetchRequest):
        """
        Fetch messages from Discord channel for specified user.
        
        Parameters can be provided in request body, or will use environment defaults.
        """
        try:
            # Fetch messages from Discord
            discord_data = await discord_service.fetch_discord_messages(request)
            
            if not discord_data:
                raise HTTPException(
                    status_code=404, 
                    detail="No messages found or failed to fetch from Discord"
                )
            
            # Save to database
            saved = await discord_service.save_to_database(discord_data)
            
            if not saved:
                logger.warning("Failed to save to database, but returning fetched data")
            
            return discord_data
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Error in fetch_discord_messages: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

    @router.get("/messages/latest",
                response_model=List[Dict[str, Any]],
                summary="Get latest messages from database",
                description="Retrieve latest Discord messages from database")
    async def get_latest_messages(limit: int = 10):
        """
        Get latest Discord messages from database.
        
        Args:
            limit: Number of records to retrieve (default: 10)
        """
        try:
            messages = await discord_service.get_latest_messages(limit)
            return messages
            
        except Exception as e:
            logger.error(f"Error in get_latest_messages: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

    @router.post("/messages/fetch-and-save",
                 summary="Fetch and save Discord messages",
                 description="Fetch messages from Discord and save to database (used by scheduler)")
    async def fetch_and_save_messages(request: DiscordFetchRequest):
        """
        Fetch messages from Discord and save to database.
        This endpoint is designed to be called by the scheduler.
        """
        try:
            # Fetch messages from Discord
            discord_data = await discord_service.fetch_discord_messages(request)
            
            if not discord_data:
                return {
                    "success": False,
                    "message": "No messages found or failed to fetch from Discord"
                }
            
            # Save to database
            saved = await discord_service.save_to_database(discord_data)
            
            return {
                "success": saved,
                "message": f"Fetched {discord_data.exported_count} messages from {discord_data.username}",
                "username": discord_data.username,
                "message_count": discord_data.exported_count,
                "total_groups": len(discord_data.message_groups)
            }
            
        except ValueError as e:
            return {
                "success": False,
                "message": f"Configuration error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Error in fetch_and_save_messages: {str(e)}")
            return {
                "success": False,
                "message": f"Internal server error: {str(e)}"
            }

    return router