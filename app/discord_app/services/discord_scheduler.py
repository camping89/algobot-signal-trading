import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.discord_app.services.discord_message_service import DiscordMessageService
from app.discord_app.models.message import DiscordFetchRequest


class DiscordScheduler:
    def __init__(self, discord_service: DiscordMessageService):
        self.scheduler = AsyncIOScheduler()
        self.discord_service = discord_service
        self.logger = logging.getLogger(__name__)
        self.job_id = "discord_message_fetch"
        
    async def start_scheduler(self):
        """Start the scheduler with Discord message fetching job"""
        try:
            # Add job to run every 1 minute
            self.scheduler.add_job(
                func=self._fetch_messages_job,
                trigger=IntervalTrigger(minutes=1),
                id=self.job_id,
                name="Fetch Discord Messages",
                replace_existing=True
            )
            
            self.scheduler.start()
            self.logger.info("Discord message scheduler started (runs every 1 minute)")
            
        except Exception as e:
            self.logger.error(f"Failed to start Discord scheduler: {str(e)}")
            raise
    
    async def stop_scheduler(self):
        """Stop the scheduler"""
        try:
            if self.scheduler.running:
                self.scheduler.shutdown(wait=True)
                self.logger.info("Discord message scheduler stopped")
        except Exception as e:
            self.logger.error(f"Error stopping Discord scheduler: {str(e)}")
    
    async def _fetch_messages_job(self):
        """Job function to fetch Discord messages"""
        try:
            self.logger.info("Starting scheduled Discord message fetch")
            
            # Create request with default values (from env)
            request = DiscordFetchRequest()
            
            # Fetch messages
            discord_data = await self.discord_service.fetch_discord_messages(request)
            
            if discord_data:
                # Save to database
                saved = await self.discord_service.save_to_database(discord_data)
                
                if saved:
                    pass
                else:
                    self.logger.error("Failed to save Discord messages to database")
            else:
                self.logger.warning("No Discord messages fetched")
                
        except Exception as e:
            self.logger.error(f"Error in scheduled Discord message fetch: {str(e)}")
    
    def is_running(self) -> bool:
        """Check if scheduler is running"""
        return self.scheduler.running if self.scheduler else False
    
    async def run_job_now(self):
        """Manually trigger the job to run immediately"""
        try:
            await self._fetch_messages_job()
        except Exception as e:
            self.logger.error(f"Error running Discord job manually: {str(e)}")
            raise