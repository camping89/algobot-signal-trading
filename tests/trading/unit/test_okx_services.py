import pytest
from unittest.mock import AsyncMock, patch, Mock
from app.trading.services.okx.okx_base_service import OKXBaseService

@pytest.mark.unit
class TestOKXBaseService:
    
    @pytest.fixture
    def okx_service(self):
        return OKXBaseService()
    
    @pytest.mark.asyncio
    async def test_connect_success(self, okx_service):
        # OKX connects successfully
        with patch('okx.api.account.Account') as mock_account:
            mock_account.return_value = Mock()
            result = await okx_service.connect("key", "secret", "passphrase", True)
            assert result is True
    
    @pytest.mark.asyncio
    async def test_connect_failure(self, okx_service):
        # OKX connection fails
        with patch('okx.api.account.Account') as mock_account:
            mock_account.side_effect = Exception("Connection error")
            result = await okx_service.connect("key", "secret", "passphrase", True)
            assert result is False

@pytest.mark.unit 
class TestOKXTradingService:
    
    @pytest.mark.asyncio
    async def test_place_order(self, sample_okx_request):
        # OKX order placed successfully
        from app.trading.services.okx.okx_trading_service import OKXTradingService
        service = OKXTradingService()
        with patch.object(service, '_place_order') as mock_place:
            mock_place.return_value = {"status": "success", "order_id": "123"}
            result = await service.place_order(sample_okx_request)
            assert result["status"] == "success"