import pytest
import asyncio
from unittest.mock import Mock, AsyncMock

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_discord_service():
    service = AsyncMock()
    service.initialize_db.return_value = None
    service.close_db_connection.return_value = None
    return service

@pytest.fixture
def mock_discord_scheduler():
    scheduler = Mock()
    scheduler.start_scheduler.return_value = None
    scheduler.stop_scheduler.return_value = None
    scheduler.is_running.return_value = True
    return scheduler

@pytest.fixture
def sample_discord_message():
    return {
        "id": "123456789",
        "content": "BUY EURUSD at 1.0850",
        "author": "test_user",
        "timestamp": "2024-01-01T00:00:00Z"
    }