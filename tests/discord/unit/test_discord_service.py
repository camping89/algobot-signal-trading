import pytest
from unittest.mock import AsyncMock, patch
from app.discord.services.discord_message_service import DiscordMessageService

@pytest.mark.unit
class TestDiscordMessageService:
    
    @pytest.fixture
    def discord_service(self):
        return DiscordMessageService()
    
    @pytest.mark.asyncio
    async def test_initialize_db(self, discord_service):
        with patch.object(discord_service, '_init_database') as mock_init:
            mock_init.return_value = None
            await discord_service.initialize_db()
            mock_init.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_close_db_connection(self, discord_service):
        discord_service.client = AsyncMock()
        await discord_service.close_db_connection()
        discord_service.client.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_fetch_messages(self, discord_service, sample_discord_message):
        with patch.object(discord_service, '_fetch_from_discord') as mock_fetch:
            mock_fetch.return_value = [sample_discord_message]
            result = await discord_service.fetch_messages(limit=10)
            assert len(result) == 1
            assert result[0]["content"] == "BUY EURUSD at 1.0850"