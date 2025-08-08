from typing import Dict, Any, List, Optional
import logging
from .okx_base_service import OKXBaseService
from app.trading_app.models.okx.trade import (
    OKXTradeRequest, OKXTradeResponse, OrderSide, 
    OKXOrder, CancelOKXOrderRequest, ModifyOKXOrderRequest,
    CloseOKXPositionRequest, CloseOKXPositionResponse
)
from tenacity import retry, stop_after_attempt, wait_exponential
import asyncio
from app.shared.utils.retry_helper import handle_retry_error
from app.shared.utils.constants import (
    MAX_RETRIES, VERIFICATION_WAIT_TIME,
    RETRY_MULTIPLIER, RETRY_MIN_WAIT, RETRY_MAX_WAIT
)

logger = logging.getLogger(__name__)

class OKXTradingService:
    """
    Service for handling trading operations in OKX.
    Provides functionality for executing trades, managing positions and orders.
    """
    def __init__(self, base_service: OKXBaseService):
        """
        Initialize trading service with base OKX connection.
        
        Parameters:
        - base_service: Base OKX service for connection management
        """
        self.base_service = base_service
        self.max_retries = MAX_RETRIES

    @property
    def initialized(self):
        """Check if trading service is initialized and connected"""
        return self.base_service.initialized

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=RETRY_MULTIPLIER, min=RETRY_MIN_WAIT, max=RETRY_MAX_WAIT),
        retry_error_callback=lambda retry_state: handle_retry_error(retry_state, max_retries=MAX_RETRIES)
    )
    async def place_order(self, trade_request: OKXTradeRequest) -> OKXTradeResponse:
        """
        Place a new order on OKX
        
        Args:
            trade_request: Trading request containing order details
            
        Returns:
            OKXTradeResponse: Order execution result with status and details
        """
        if not await self.base_service.ensure_connected():
            return OKXTradeResponse(
                ord_id="",
                s_code="1",
                s_msg="Failed to connect to OKX API"
            )

        try:
            # Prepare order parameters
            order_params = {
                "instId": trade_request.inst_id,
                "tdMode": trade_request.td_mode.value,
                "side": trade_request.side.value,
                "ordType": trade_request.ord_type,
                "sz": trade_request.sz,
            }
            
            if trade_request.px:
                order_params["px"] = trade_request.px
            
            if trade_request.ccy:
                order_params["ccy"] = trade_request.ccy
                
            if trade_request.cl_ord_id:
                order_params["clOrdId"] = trade_request.cl_ord_id
                
            if trade_request.tag:
                order_params["tag"] = trade_request.tag
                
            if trade_request.pos_side:
                order_params["posSide"] = trade_request.pos_side.value
                
            if trade_request.reduce_only is not None:
                order_params["reduceOnly"] = trade_request.reduce_only
                
            if trade_request.tp_trigger_px:
                order_params["tpTriggerPx"] = trade_request.tp_trigger_px
                
            if trade_request.tp_ord_px:
                order_params["tpOrdPx"] = trade_request.tp_ord_px
                
            if trade_request.sl_trigger_px:
                order_params["slTriggerPx"] = trade_request.sl_trigger_px
                
            if trade_request.sl_ord_px:
                order_params["slOrdPx"] = trade_request.sl_ord_px
                
            if trade_request.tp_trigger_px_type:
                order_params["tpTriggerPxType"] = trade_request.tp_trigger_px_type
                
            if trade_request.sl_trigger_px_type:
                order_params["slTriggerPxType"] = trade_request.sl_trigger_px_type
                
            if trade_request.quick_margin_type:
                order_params["quickMgnType"] = trade_request.quick_margin_type
                
            if trade_request.stp_id:
                order_params["stpId"] = trade_request.stp_id
                
            if trade_request.stp_mode:
                order_params["stpMode"] = trade_request.stp_mode
                
            if trade_request.banner_flag:
                order_params["bannerFlag"] = trade_request.banner_flag

            # Execute the trade
            result = self.base_service.trade_api.set_order(**order_params)
            
            if not result or 'data' not in result or not result['data']:
                error_msg = result.get('msg', 'Unknown error') if result else 'No response'
                logger.error(f"Order failed: {error_msg}")
                return OKXTradeResponse(
                    ord_id="",
                    s_code="1", 
                    s_msg=f"Order failed: {error_msg}"
                )

            order_data = result['data'][0]
            
            # Check if order was successfully placed
            if order_data['sCode'] != '0':
                logger.error(f"Order failed: {order_data['sMsg']}")
                return OKXTradeResponse(
                    ord_id=order_data.get('ordId', ''),
                    cl_ord_id=order_data.get('clOrdId'),
                    tag=order_data.get('tag'),
                    s_code=order_data['sCode'],
                    s_msg=order_data['sMsg']
                )

            logger.info(f"Order placed successfully: Order ID {order_data['ordId']}")
            return OKXTradeResponse(
                ord_id=order_data['ordId'],
                cl_ord_id=order_data.get('clOrdId'),
                tag=order_data.get('tag'),
                s_code=order_data['sCode'],
                s_msg=order_data['sMsg']
            )

        except Exception as e:
            logger.error(f"Error placing order: {str(e)}")
            return OKXTradeResponse(
                ord_id="",
                s_code="1",
                s_msg=str(e)
            )

    async def cancel_order(self, cancel_request: CancelOKXOrderRequest) -> OKXTradeResponse:
        """
        Cancel an existing order
        
        Args:
            cancel_request: Cancel order request
            
        Returns:
            OKXTradeResponse: Cancellation result
        """
        if not await self.base_service.ensure_connected():
            return OKXTradeResponse(
                ord_id="",
                s_code="1",
                s_msg="Failed to connect to OKX API"
            )

        try:
            cancel_params = {
                "instId": cancel_request.inst_id
            }
            
            if cancel_request.ord_id:
                cancel_params["ordId"] = cancel_request.ord_id
            elif cancel_request.cl_ord_id:
                cancel_params["clOrdId"] = cancel_request.cl_ord_id
            else:
                return OKXTradeResponse(
                    ord_id="",
                    s_code="1",
                    s_msg="Either ordId or clOrdId must be provided"
                )

            result = self.base_service.trade_api.set_cancel_order(**cancel_params)
            
            if not result or 'data' not in result or not result['data']:
                error_msg = result.get('msg', 'Unknown error') if result else 'No response'
                return OKXTradeResponse(
                    ord_id="",
                    s_code="1",
                    s_msg=f"Cancel failed: {error_msg}"
                )

            cancel_data = result['data'][0]
            
            return OKXTradeResponse(
                ord_id=cancel_data.get('ordId', ''),
                cl_ord_id=cancel_data.get('clOrdId'),
                s_code=cancel_data['sCode'],
                s_msg=cancel_data['sMsg']
            )

        except Exception as e:
            logger.error(f"Error canceling order: {str(e)}")
            return OKXTradeResponse(
                ord_id="",
                s_code="1",
                s_msg=str(e)
            )

    async def modify_order(self, modify_request: ModifyOKXOrderRequest) -> OKXTradeResponse:
        """
        Modify an existing order
        
        Args:
            modify_request: Modify order request
            
        Returns:
            OKXTradeResponse: Modification result
        """
        if not await self.base_service.ensure_connected():
            return OKXTradeResponse(
                ord_id="",
                s_code="1", 
                s_msg="Failed to connect to OKX API"
            )

        try:
            modify_params = {
                "instId": modify_request.inst_id
            }
            
            if modify_request.ord_id:
                modify_params["ordId"] = modify_request.ord_id
            elif modify_request.cl_ord_id:
                modify_params["clOrdId"] = modify_request.cl_ord_id
            else:
                return OKXTradeResponse(
                    ord_id="",
                    s_code="1",
                    s_msg="Either ordId or clOrdId must be provided"
                )
                
            if modify_request.new_sz:
                modify_params["newSz"] = modify_request.new_sz
                
            if modify_request.new_px:
                modify_params["newPx"] = modify_request.new_px
                
            if modify_request.req_id:
                modify_params["reqId"] = modify_request.req_id

            result = self.base_service.trade_api.set_amend_order(**modify_params)
            
            if not result or 'data' not in result or not result['data']:
                error_msg = result.get('msg', 'Unknown error') if result else 'No response'
                return OKXTradeResponse(
                    ord_id="",
                    s_code="1",
                    s_msg=f"Modify failed: {error_msg}"
                )

            modify_data = result['data'][0]
            
            return OKXTradeResponse(
                ord_id=modify_data.get('ordId', ''),
                cl_ord_id=modify_data.get('clOrdId'),
                s_code=modify_data['sCode'],
                s_msg=modify_data['sMsg']
            )

        except Exception as e:
            logger.error(f"Error modifying order: {str(e)}")
            return OKXTradeResponse(
                ord_id="",
                s_code="1",
                s_msg=str(e)
            )

    async def get_orders(self, inst_id: str = None, ult_type: str = "SPOT", state: str = None, limit: str = "100") -> List[OKXOrder]:
        """
        Get order history
        
        Args:
            inst_id: Instrument ID filter
            ult_type: Underlying type (SPOT, MARGIN, SWAP, FUTURES, OPTION)
            state: Order state filter
            limit: Number of results to return
            
        Returns:
            List[OKXOrder]: List of orders
        """
        if not await self.base_service.ensure_connected():
            return []

        try:
            params = {
                "limit": limit
            }
            
            if inst_id:
                params["instId"] = inst_id
            if state:
                params["state"] = state
                
            params["instType"] = ult_type

            result = self.base_service.trade_api.get_orders_history(**params)
            
            if not result or 'data' not in result:
                return []

            orders = []
            for order_data in result['data']:
                try:
                    order = OKXOrder(**order_data)
                    orders.append(order)
                except Exception as e:
                    logger.warning(f"Failed to parse order data: {e}")
                    continue
                    
            return orders

        except Exception as e:
            logger.error(f"Error getting orders: {str(e)}")
            return []

    async def get_order_details(self, inst_id: str, ord_id: str = None, cl_ord_id: str = None) -> Optional[OKXOrder]:
        """
        Get details of a specific order
        
        Args:
            inst_id: Instrument ID
            ord_id: Order ID
            cl_ord_id: Client order ID
            
        Returns:
            Optional[OKXOrder]: Order details if found
        """
        if not await self.base_service.ensure_connected():
            return None

        try:
            params = {
                "instId": inst_id
            }
            
            if ord_id:
                params["ordId"] = ord_id
            elif cl_ord_id:
                params["clOrdId"] = cl_ord_id
            else:
                return None

            result = self.base_service.trade_api.get_order(**params)
            
            if not result or 'data' not in result or not result['data']:
                return None

            order_data = result['data'][0]
            return OKXOrder(**order_data)

        except Exception as e:
            logger.error(f"Error getting order details: {str(e)}")
            return None

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=RETRY_MULTIPLIER, min=RETRY_MIN_WAIT, max=RETRY_MAX_WAIT),
        retry_error_callback=lambda retry_state: handle_retry_error(retry_state, max_retries=MAX_RETRIES)
    )
    async def close_position(self, close_request: CloseOKXPositionRequest) -> CloseOKXPositionResponse:
        """
        Close position using market order
        
        Args:
            close_request: Close position request
            
        Returns:
            CloseOKXPositionResponse: Close position result
        """
        if not await self.base_service.ensure_connected():
            logger.error("Failed to connect to OKX API")
            return CloseOKXPositionResponse(
                inst_id=close_request.inst_id,
                pos_side=close_request.pos_side,
                cl_ord_id=close_request.cl_ord_id,
                tag=close_request.tag
            )

        try:
            close_params = {
                "instId": close_request.inst_id,
                "mgnMode": close_request.mgn_mode
            }
            
            if close_request.pos_side:
                close_params["posSide"] = close_request.pos_side
                
            if close_request.ccy:
                close_params["ccy"] = close_request.ccy
                
            if close_request.auto_cxl is not None:
                close_params["autoCxl"] = close_request.auto_cxl
                
            if close_request.cl_ord_id:
                close_params["clOrdId"] = close_request.cl_ord_id
                
            if close_request.tag:
                close_params["tag"] = close_request.tag

            result = self.base_service.trade_api.set_close_position(**close_params)
            
            if not result or 'data' not in result or not result['data']:
                error_msg = result.get('msg', 'Unknown error') if result else 'No response'
                logger.error(f"Close position failed: {error_msg}")
                return CloseOKXPositionResponse(
                    inst_id=close_request.inst_id,
                    pos_side=close_request.pos_side,
                    cl_ord_id=close_request.cl_ord_id,
                    tag=close_request.tag
                )

            close_data = result['data'][0]
            
            logger.info(f"Position closed successfully for {close_request.inst_id}")
            return CloseOKXPositionResponse(
                inst_id=close_data.get('instId', close_request.inst_id),
                pos_side=close_data.get('posSide', close_request.pos_side),
                cl_ord_id=close_data.get('clOrdId', close_request.cl_ord_id),
                tag=close_data.get('tag', close_request.tag)
            )

        except Exception as e:
            logger.error(f"Error closing position: {str(e)}")
            return CloseOKXPositionResponse(
                inst_id=close_request.inst_id,
                pos_side=close_request.pos_side,
                cl_ord_id=close_request.cl_ord_id,
                tag=close_request.tag
            )