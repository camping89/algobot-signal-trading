from typing import List, Optional, Dict, Any
import logging
from .okx_base_service import OKXBaseService
from app.trading_app.models.okx.account import (
    OKXAccount, OKXAccountConfig, OKXBalance, OKXLeverage, OKXMaxSize,
    OKXMaxAvailSize, OKXMarginBalance, OKXGreeks,
    OKXFeeRate, OKXPositionMode, OKXMarginMode
)
from app.trading_app.models.okx.trade import OKXPosition

logger = logging.getLogger(__name__)

class OKXAccountService:
    """
    Service for handling account operations in OKX.
    Provides functionality for account information, balances, and positions.
    """
    
    def __init__(self, base_service: OKXBaseService):
        """
        Initialize account service with base OKX connection.
        
        Parameters:
        - base_service: Base OKX service for connection management
        """
        self.base_service = base_service

    @property
    def initialized(self):
        """Check if account service is initialized and connected"""
        return self.base_service.initialized

    async def get_account_info(self) -> Optional[OKXAccount]:
        """
        Get account balance information
        
        Returns:
            Optional[OKXAccount]: Account balance information if successful
        """
        if not await self.base_service.ensure_connected():
            return None

        try:
            result = self.base_service.account_api.get_balance()
            
            if not result or 'data' not in result or not result['data']:
                logger.error("No account balance data returned")
                return None

            account_data = result['data'][0]
            return OKXAccount(**account_data)

        except Exception as e:
            logger.error(f"Error getting account info: {str(e)}")
            return None

    async def get_account_config(self) -> Optional[OKXAccountConfig]:
        """
        Get account configuration
        
        Returns:
            Optional[OKXAccountConfig]: Account configuration if successful
        """
        if not await self.base_service.ensure_connected():
            return None

        try:
            result = self.base_service.account_api.get_config()
            
            if not result or 'data' not in result or not result['data']:
                logger.error("No account config data returned")
                return None

            config_data = result['data'][0]
            return OKXAccountConfig(**config_data)

        except Exception as e:
            logger.error(f"Error getting account config: {str(e)}")
            return None

    async def get_balances(self, ccy: str = None) -> List[OKXBalance]:
        """
        Get account balances
        
        Args:
            ccy: Currency filter (optional)
            
        Returns:
            List[OKXBalance]: List of balances
        """
        if not await self.base_service.ensure_connected():
            return []

        try:
            params = {}
            if ccy:
                params["ccy"] = ccy

            result = self.base_service.account_api.get_balance(**params)
            
            if not result or 'data' not in result or not result['data']:
                return []

            balances = []
            for balance_data in result['data'][0]['details']:
                try:
                    # Add the update time from parent data
                    balance_data['u_time'] = result['data'][0]['uTime']
                    balance = OKXBalance(**balance_data)
                    balances.append(balance)
                except Exception as e:
                    logger.warning(f"Failed to parse balance data: {e}")
                    continue
                    
            return balances

        except Exception as e:
            logger.error(f"Error getting balances: {str(e)}")
            return []

    async def get_positions(self, inst_type: str = None, inst_id: str = None) -> List[OKXPosition]:
        """
        Get account positions
        
        Args:
            inst_type: Instrument type filter (MARGIN, SWAP, FUTURES, OPTION)
            inst_id: Instrument ID filter
            
        Returns:
            List[OKXPosition]: List of positions
        """
        if not await self.base_service.ensure_connected():
            return []

        try:
            params = {}
            if inst_type:
                params["instType"] = inst_type
            if inst_id:
                params["instId"] = inst_id

            result = self.base_service.account_api.get_positions(**params)
            
            if not result or 'data' not in result:
                return []

            positions = []
            for pos_data in result['data']:
                try:
                    position = OKXPosition(**pos_data)
                    positions.append(position)
                except Exception as e:
                    logger.warning(f"Failed to parse position data: {e}")
                    continue
                    
            return positions

        except Exception as e:
            logger.error(f"Error getting positions: {str(e)}")
            return []

    async def get_leverage(self, inst_id: str, mgn_mode: str) -> Optional[OKXLeverage]:
        """
        Get leverage information
        
        Args:
            inst_id: Instrument ID
            mgn_mode: Margin mode (isolated, cross)
            
        Returns:
            Optional[OKXLeverage]: Leverage information
        """
        if not await self.base_service.ensure_connected():
            return None

        try:
            result = self.base_service.account_api.get_leverage(
                instId=inst_id,
                mgnMode=mgn_mode
            )
            
            if not result or 'data' not in result or not result['data']:
                return None

            leverage_data = result['data'][0]
            return OKXLeverage(**leverage_data)

        except Exception as e:
            logger.error(f"Error getting leverage for {inst_id}: {str(e)}")
            return None

    async def set_leverage(self, inst_id: str, lever: str, mgn_mode: str, pos_side: str = None) -> bool:
        """
        Set leverage for an instrument
        
        Args:
            inst_id: Instrument ID
            lever: Leverage value
            mgn_mode: Margin mode (isolated, cross)
            pos_side: Position side (long, short, net)
            
        Returns:
            bool: True if successful
        """
        if not await self.base_service.ensure_connected():
            return False

        try:
            params = {
                "instId": inst_id,
                "lever": lever,
                "mgnMode": mgn_mode
            }
            
            if pos_side:
                params["posSide"] = pos_side

            result = self.base_service.account_api.set_leverage(**params)
            
            if not result or 'data' not in result:
                return False

            return result['data'][0]['sCode'] == '0'

        except Exception as e:
            logger.error(f"Error setting leverage for {inst_id}: {str(e)}")
            return False

    async def get_max_size(self, inst_id: str, td_mode: str, ccy: str = None, px: str = None) -> Optional[OKXMaxSize]:
        """
        Get maximum tradable size
        
        Args:
            inst_id: Instrument ID
            td_mode: Trade mode (cash, cross, isolated)
            ccy: Currency
            px: Price
            
        Returns:
            Optional[OKXMaxSize]: Maximum size information
        """
        if not await self.base_service.ensure_connected():
            return None

        try:
            params = {
                "instId": inst_id,
                "tdMode": td_mode
            }
            
            if ccy:
                params["ccy"] = ccy
            if px:
                params["px"] = px

            result = self.base_service.account_api.get_max_size(**params)
            
            if not result or 'data' not in result or not result['data']:
                return None

            max_size_data = result['data'][0]
            return OKXMaxSize(**max_size_data)

        except Exception as e:
            logger.error(f"Error getting max size for {inst_id}: {str(e)}")
            return None

    async def get_max_avail_size(self, inst_id: str, td_mode: str, ccy: str = None, reduce_only: bool = None) -> Optional[OKXMaxAvailSize]:
        """
        Get maximum available size
        
        Args:
            inst_id: Instrument ID
            td_mode: Trade mode (cash, cross, isolated)
            ccy: Currency
            reduce_only: Reduce only flag
            
        Returns:
            Optional[OKXMaxAvailSize]: Maximum available size information
        """
        if not await self.base_service.ensure_connected():
            return None

        try:
            params = {
                "instId": inst_id,
                "tdMode": td_mode
            }
            
            if ccy:
                params["ccy"] = ccy
            if reduce_only is not None:
                params["reduceOnly"] = reduce_only

            result = self.base_service.account_api.get_max_avail_size(**params)
            
            if not result or 'data' not in result or not result['data']:
                return None

            max_avail_data = result['data'][0]
            return OKXMaxAvailSize(**max_avail_data)

        except Exception as e:
            logger.error(f"Error getting max avail size for {inst_id}: {str(e)}")
            return None

    async def get_fee_rates(self, inst_type: str, inst_id: str = None, uly: str = None, inst_family: str = None) -> List[OKXFeeRate]:
        """
        Get trading fee rates
        
        Args:
            inst_type: Instrument type (SPOT, MARGIN, SWAP, FUTURES, OPTION)
            inst_id: Instrument ID
            uly: Underlying
            inst_family: Instrument family
            
        Returns:
            List[OKXFeeRate]: List of fee rates
        """
        if not await self.base_service.ensure_connected():
            return []

        try:
            params = {
                "instType": inst_type
            }
            
            if inst_id:
                params["instId"] = inst_id
            if uly:
                params["uly"] = uly
            if inst_family:
                params["instFamily"] = inst_family

            result = self.base_service.account_api.get_fee_rates(**params)
            
            if not result or 'data' not in result:
                return []

            fee_rates = []
            for fee_data in result['data']:
                try:
                    fee_rate = OKXFeeRate(**fee_data)
                    fee_rates.append(fee_rate)
                except Exception as e:
                    logger.warning(f"Failed to parse fee rate data: {e}")
                    continue
                    
            return fee_rates

        except Exception as e:
            logger.error(f"Error getting fee rates: {str(e)}")
            return []

    async def get_position_mode(self) -> Optional[str]:
        """
        Get account position mode
        
        Returns:
            Optional[str]: Position mode (long_short_mode or net_mode)
        """
        if not await self.base_service.ensure_connected():
            return None

        try:
            result = self.base_service.account_api.get_position_mode()
            
            if not result or 'data' not in result or not result['data']:
                return None

            return result['data'][0]['posMode']

        except Exception as e:
            logger.error(f"Error getting position mode: {str(e)}")
            return None

    async def set_position_mode(self, pos_mode: str) -> bool:
        """
        Set account position mode
        
        Args:
            pos_mode: Position mode (long_short_mode or net_mode)
            
        Returns:
            bool: True if successful
        """
        if not await self.base_service.ensure_connected():
            return False

        try:
            result = self.base_service.account_api.set_position_mode(posMode=pos_mode)
            
            if not result or 'data' not in result:
                return False

            return result['data'][0]['sCode'] == '0'

        except Exception as e:
            logger.error(f"Error setting position mode: {str(e)}")
            return False