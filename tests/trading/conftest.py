import pytest
import asyncio
from unittest.mock import Mock, AsyncMock

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_okx_service():
    service = AsyncMock()
    service.initialized = True
    service.connect.return_value = True
    service.ensure_connected.return_value = True
    return service

@pytest.fixture
def sample_trade_request():
    return {
        "symbol": "EURUSD",
        "order_type": "BUY",
        "amount": 0.1,
        "stop_loss": 1.0800,
        "take_profit": 1.0900
    }

@pytest.fixture
def sample_okx_request():
    return {
        "inst_id": "BTC-USDT",
        "td_mode": "cash",
        "side": "buy",
        "ord_type": "limit",
        "sz": "0.001",
        "px": "45000"
    }