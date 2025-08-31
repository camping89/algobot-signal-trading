"""Refactored OKX Trading Service with enhanced error handling."""

from typing import Dict, Any, List, Optional
import logging
import asyncio

from .okx_base_service import OKXBaseService
from app.trading.models.okx.trade import (
    OKXTradeRequest, OKXTradeResponse, OrderSide, 
    OKXOrder, CancelOKXOrderRequest, ModifyOKXOrderRequest,
    CloseOKXPositionRequest, CloseOKXPositionResponse
)
from shared.error_handler import (
    with_error_handling, error_context,
    STANDARD_RETRY, CONNECTION_RETRY
)
from shared.services.exceptions import (
    OKXConnectionError, OKXAPIError, RateLimitError,
    ValidationError, ServiceNotInitializedError,
    TradeExecutionError, OrderNotFoundError,
    PositionNotFoundError, InsufficientFundsError,
    AuthenticationError
)
from shared.utils.constants import VERIFICATION_WAIT_TIME

logger = logging.getLogger(__name__)


class OKXTradingServiceRefactored:
    """
    Refactored service for handling trading operations in OKX with enhanced error handling.
    Provides functionality for executing trades, managing positions and orders.
    """
    
    def __init__(self, base_service: OKXBaseService):
        """
        Initialize trading service with base OKX connection.
        
        Args:
            base_service: Base OKX service for connection management
        """
        self.base_service = base_service
        self.logger = logging.getLogger(self.__class__.__name__)

    @property
    def initialized(self) -> bool:
        """Check if trading service is initialized and connected."""
        return self.base_service.initialized

    async def _ensure_connection(self) -> None:
        """Ensure OKX connection is active, raise exception if not."""
        if not await self.base_service.ensure_connected():
            raise ServiceNotInitializedError("Failed to establish OKX API connection")

    def _validate_trade_request(self, trade_request: OKXTradeRequest) -> None:
        """Validate trade request parameters."""
        if not trade_request.inst_id:
            raise ValidationError("Instrument ID is required")
        
        if not trade_request.sz or float(trade_request.sz) <= 0:
            raise ValidationError(f"Invalid order size: {trade_request.sz}")
        
        if trade_request.px and float(trade_request.px) <= 0:
            raise ValidationError(f"Invalid price: {trade_request.px}")

    def _handle_okx_response(self, response: dict, operation: str) -> None:
        """Handle OKX API response and raise appropriate exceptions."""
        if not isinstance(response, dict):
            raise OKXAPIError(f"Invalid response format for {operation}")
        
        code = response.get('code', '1')
        msg = response.get('msg', 'Unknown error')
        
        if code != '0':
            error_msg = f"OKX API error in {operation}: {msg} (code: {code})"
            
            # Map specific error codes to appropriate exceptions
            if code in ['50001', '50002', '50003']:  # Authentication errors
                raise AuthenticationError(error_msg)
            elif code in ['50004', '50005']:  # Rate limit errors
                raise RateLimitError(error_msg)
            elif code in ['51008', '51009']:  # Insufficient balance
                raise InsufficientFundsError(error_msg)
            elif code in ['51001', '51002']:  # Invalid instrument
                raise ValidationError(error_msg)
            elif code in ['51117', '51118']:  # Order not found
                raise OrderNotFoundError(error_msg)
            else:
                raise OKXAPIError(error_msg)

    @with_error_handling(
        operation="place_order",
        retry_config=CONNECTION_RETRY,
        fallback_return=OKXTradeResponse(
            ord_id="",
            s_code="1",
            s_msg="Order placement failed"
        ),
        reraise=False
    )
    async def place_order(self, trade_request: OKXTradeRequest) -> OKXTradeResponse:
        """
        Place a new order on OKX.
        
        Args:
            trade_request: Trading request containing order details
            
        Returns:
            OKXTradeResponse: Order execution result with status and details
            
        Raises:
            ServiceNotInitializedError: If OKX connection is not available
            ValidationError: If trade parameters are invalid
            InsufficientFundsError: If insufficient balance
            RateLimitError: If rate limit exceeded
            TradeExecutionError: If order placement fails
        """
        await self._ensure_connection()
        self._validate_trade_request(trade_request)

        # Prepare order parameters
        order_params = self._prepare_order_params(trade_request)
        
        # Place order via OKX API
        with error_context('OKXTradingService', 'place_order', symbol=trade_request.inst_id):
            result = self.base_service.trade_api.place_order(**order_params)
            self._handle_okx_response(result, 'place_order')
            
            order_data = result.get('data', [])
            if not order_data:
                raise TradeExecutionError("No order data returned from OKX API")
            
            order_info = order_data[0]
            ord_id = order_info.get('ordId', '')
            s_code = order_info.get('sCode', '0')
            s_msg = order_info.get('sMsg', '')
            
            if s_code != '0':
                error_msg = f"Order placement failed: {s_msg} (code: {s_code})"
                raise TradeExecutionError(error_msg)
            
            if not ord_id:
                raise TradeExecutionError("No order ID returned from successful order placement")

        self.logger.info(f"Order placed successfully on OKX: Order ID {ord_id}")
        return OKXTradeResponse(
            ord_id=ord_id,
            s_code=s_code,
            s_msg=s_msg or "Order placed successfully"
        )

    def _prepare_order_params(self, trade_request: OKXTradeRequest) -> Dict[str, Any]:
        """Prepare order parameters for OKX API."""
        order_params = {
            "instId": trade_request.inst_id,
            "tdMode": trade_request.td_mode.value,
            "side": trade_request.side.value,
            "ordType": trade_request.ord_type,
            "sz": trade_request.sz,
        }
        
        # Add optional parameters
        if trade_request.px:
            order_params["px"] = trade_request.px
        
        if trade_request.ccy:
            order_params["ccy"] = trade_request.ccy
            
        if trade_request.cl_ord_id:
            order_params["clOrdId"] = trade_request.cl_ord_id
            
        if trade_request.tag:
            order_params["tag"] = trade_request.tag
        
        return order_params

    @with_error_handling(
        operation="cancel_order",
        retry_config=STANDARD_RETRY,
        fallback_return=OKXTradeResponse(
            ord_id="",
            s_code="1",
            s_msg="Order cancellation failed"
        ),
        reraise=False
    )
    async def cancel_order(self, cancel_request: CancelOKXOrderRequest) -> OKXTradeResponse:
        """
        Cancel an existing order.
        
        Args:
            cancel_request: Order cancellation request
            
        Returns:
            OKXTradeResponse: Cancellation result
            
        Raises:
            ServiceNotInitializedError: If OKX connection is not available
            ValidationError: If request parameters are invalid
            OrderNotFoundError: If order not found
        """
        await self._ensure_connection()
        
        if not cancel_request.ord_id and not cancel_request.cl_ord_id:
            raise ValidationError("Either order ID or client order ID is required for cancellation")

        cancel_params = {
            "instId": cancel_request.inst_id,
        }
        
        if cancel_request.ord_id:
            cancel_params["ordId"] = cancel_request.ord_id
        if cancel_request.cl_ord_id:
            cancel_params["clOrdId"] = cancel_request.cl_ord_id

        with error_context('OKXTradingService', 'cancel_order', 
                          symbol=cancel_request.inst_id, order_id=cancel_request.ord_id):
            result = self.base_service.trade_api.cancel_order(**cancel_params)
            self._handle_okx_response(result, 'cancel_order')
            
            cancel_data = result.get('data', [])
            if not cancel_data:
                raise TradeExecutionError("No cancellation data returned from OKX API")
            
            cancel_info = cancel_data[0]
            ord_id = cancel_info.get('ordId', cancel_request.ord_id)
            s_code = cancel_info.get('sCode', '0')
            s_msg = cancel_info.get('sMsg', '')
            
            if s_code != '0':
                if s_code in ['51117', '51118']:  # Order not found
                    raise OrderNotFoundError(f"Order not found: {s_msg}")
                else:
                    raise TradeExecutionError(f"Order cancellation failed: {s_msg} (code: {s_code})")

        self.logger.info(f"Order cancelled successfully: Order ID {ord_id}")
        return OKXTradeResponse(
            ord_id=ord_id,
            s_code=s_code,
            s_msg=s_msg or "Order cancelled successfully"
        )

    @with_error_handling(
        operation="get_orders",
        retry_config=STANDARD_RETRY,
        fallback_return=[],
        reraise=False
    )
    async def get_orders(self, inst_id: Optional[str] = None, 
                        ord_type: Optional[str] = None,
                        state: Optional[str] = None) -> List[OKXOrder]:
        """
        Get list of orders with optional filters.
        
        Args:
            inst_id: Instrument ID filter
            ord_type: Order type filter
            state: Order state filter
            
        Returns:
            List[OKXOrder]: List of orders
            
        Raises:
            ServiceNotInitializedError: If OKX connection is not available
        """
        await self._ensure_connection()

        params = {}
        if inst_id:
            params["instId"] = inst_id
        if ord_type:
            params["ordType"] = ord_type
        if state:
            params["state"] = state

        with error_context('OKXTradingService', 'get_orders', symbol=inst_id):
            result = self.base_service.trade_api.get_orders(**params) if params else self.base_service.trade_api.get_orders()
            self._handle_okx_response(result, 'get_orders')
            
            orders_data = result.get('data', [])
            orders = []
            
            for order_data in orders_data:
                try:
                    # Validate required fields before creating order object
                    if not all(key in order_data for key in ['ordId', 'instId', 'side', 'ordType']):
                        self.logger.warning(f"Incomplete order data, skipping: {order_data}")
                        continue
                        
                    order = OKXOrder(**order_data)
                    orders.append(order)
                except (ValueError, TypeError) as e:
                    self.logger.warning(f"Failed to parse order data: {e}")
                    continue

        self.logger.debug(f"Retrieved {len(orders)} orders from OKX")
        return orders

    @with_error_handling(
        operation="get_order_details",
        retry_config=STANDARD_RETRY,
        fallback_return=None,
        reraise=False
    )
    async def get_order_details(self, ord_id: str, inst_id: str) -> Optional[OKXOrder]:
        """
        Get details of a specific order.
        
        Args:
            ord_id: Order ID
            inst_id: Instrument ID
            
        Returns:
            Optional[OKXOrder]: Order details or None if not found
            
        Raises:
            ServiceNotInitializedError: If OKX connection is not available
            ValidationError: If parameters are invalid
        """
        await self._ensure_connection()
        
        if not ord_id or not inst_id:
            raise ValidationError("Order ID and Instrument ID are required")

        with error_context('OKXTradingService', 'get_order_details', 
                          symbol=inst_id, order_id=ord_id):
            result = self.base_service.trade_api.get_order(ordId=ord_id, instId=inst_id)
            self._handle_okx_response(result, 'get_order_details')
            
            order_data_list = result.get('data', [])
            if not order_data_list:
                raise OrderNotFoundError(f"Order not found: {ord_id}")
            
            order_data = order_data_list[0]
            
            # Validate order data
            if not all(key in order_data for key in ['ordId', 'instId', 'side', 'ordType']):
                raise OKXAPIError(f"Incomplete order data received for order {ord_id}")

        self.logger.debug(f"Retrieved order details: {ord_id}")
        return OKXOrder(**order_data)

    @with_error_handling(
        operation="close_position",
        retry_config=CONNECTION_RETRY,
        fallback_return=CloseOKXPositionResponse(
            inst_id="",
            success=False,
            message="Position closure failed"
        ),
        reraise=False
    )
    async def close_position(self, close_request: CloseOKXPositionRequest) -> CloseOKXPositionResponse:
        """
        Close an existing position.
        
        Args:
            close_request: Position closure request
            
        Returns:
            CloseOKXPositionResponse: Closure result
            
        Raises:
            ServiceNotInitializedError: If OKX connection is not available
            ValidationError: If request parameters are invalid
            PositionNotFoundError: If position not found
        """
        await self._ensure_connection()
        
        if not close_request.inst_id:
            raise ValidationError("Instrument ID is required for position closure")
        
        if close_request.sz and float(close_request.sz) <= 0:
            raise ValidationError(f"Invalid size for position closure: {close_request.sz}")

        close_params = {
            "instId": close_request.inst_id,
            "mgnMode": close_request.mgn_mode.value,
        }
        
        if close_request.sz:
            close_params["sz"] = close_request.sz
        if close_request.px:
            close_params["px"] = close_request.px
        if close_request.ccy:
            close_params["ccy"] = close_request.ccy

        with error_context('OKXTradingService', 'close_position', symbol=close_request.inst_id):
            result = self.base_service.trade_api.close_position(**close_params)
            self._handle_okx_response(result, 'close_position')
            
            close_data = result.get('data', [])
            if not close_data:
                raise TradeExecutionError("No position closure data returned from OKX API")
            
            close_info = close_data[0]
            inst_id = close_info.get('instId', close_request.inst_id)
            s_code = close_info.get('sCode', '0')
            s_msg = close_info.get('sMsg', '')
            
            success = s_code == '0'
            if not success and s_code in ['51119', '51120']:  # Position not found
                raise PositionNotFoundError(f"Position not found: {s_msg}")

        message = s_msg or ("Position closed successfully" if success else "Position closure failed")
        self.logger.info(f"Position closure result for {inst_id}: {message}")
        
        return CloseOKXPositionResponse(
            inst_id=inst_id,
            success=success,
            message=message
        )