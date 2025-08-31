import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.discord.services.discord_scheduler import DiscordScheduler

@pytest.mark.unit
class TestDiscordScheduler:
    
    @pytest.fixture
    def scheduler(self, mock_discord_service):
        return DiscordScheduler(mock_discord_service)
    
    @pytest.mark.asyncio
    async def test_start_scheduler(self, scheduler):
        # Scheduler starts successfully
        with patch('app.discord.services.discord_scheduler.AsyncIOScheduler') as mock_sched:
            mock_instance = AsyncMock()
            mock_sched.return_value = mock_instance
            await scheduler.start_scheduler()
            mock_instance.start.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_stop_scheduler(self, scheduler):
        # Scheduler stops successfully
        scheduler.scheduler = AsyncMock()
        await scheduler.stop_scheduler()
        scheduler.scheduler.shutdown.assert_called_once()
    
    def test_is_running(self, scheduler):
        # Returns correct running status
        scheduler.scheduler = Mock()
        scheduler.scheduler.running = True
        assert scheduler.is_running() is True