from typing import Dict, Any, List, Optional
import logging
from .okx_base_service import OKXBaseService
from app.trading_app.models.okx.algo_trade import (
    OKXAlgoOrderRequest, OKXAlgoOrderResponse, OKXAlgoOrder,
    OKXTPSLOrderRequest, OKXTriggerOrderRequest, OKXTrailingStopRequest,
    OKXIcebergOrderRequest, OKXTWAPOrderRequest,
    CancelAlgoOrderRequest, AmendAlgoOrderRequest,
    AlgoOrderState
)
from tenacity import retry, stop_after_attempt, wait_exponential
from app.shared.utils.retry_helper import handle_retry_error
from app.shared.utils.constants import (
    MAX_RETRIES, VERIFICATION_WAIT_TIME,
    RETRY_MULTIPLIER, RETRY_MIN_WAIT, RETRY_MAX_WAIT
)

logger = logging.getLogger(__name__)

class OKXAlgoService:
    """
    Service for handling algorithmic trading operations in OKX.
    Supports TP/SL, Trigger, Trailing Stop, Iceberg, and TWAP orders.
    """
    def __init__(self, base_service: OKXBaseService):
        """
        Initialize algo trading service with base OKX connection.
        
        Parameters:
        - base_service: Base OKX service for connection management
        """
        self.base_service = base_service
        self.max_retries = MAX_RETRIES

    @property
    def initialized(self):
        """Check if algo trading service is initialized and connected"""
        return self.base_service.initialized

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=RETRY_MULTIPLIER, min=RETRY_MIN_WAIT, max=RETRY_MAX_WAIT),
        retry_error_callback=lambda retry_state: handle_retry_error(retry_state, max_retries=MAX_RETRIES)
    )
    async def place_tp_sl_order(self, request: OKXTPSLOrderRequest) -> OKXAlgoOrderResponse:
        """
        Place a Take Profit / Stop Loss order
        
        Args:
            request: TP/SL order request
            
        Returns:
            OKXAlgoOrderResponse: Order execution result
        """
        if not await self.base_service.ensure_connected():
            return OKXAlgoOrderResponse(
                algo_id="",
                s_code="1",
                s_msg="Failed to connect to OKX API"
            )

        try:
            order_params = {
                "instId": request.inst_id,
                "tdMode": request.td_mode.value,
                "side": request.side.value,
                "ordType": request.ord_type.value,
                "sz": request.sz,
            }
            
            if request.pos_side:
                order_params["posSide"] = request.pos_side.value
            if request.reduce_only is not None:
                order_params["reduceOnly"] = request.reduce_only
            if request.tag:
                order_params["tag"] = request.tag
            if request.cl_ord_id:
                order_params["clOrdId"] = request.cl_ord_id
            if request.tp_trigger_px:
                order_params["tpTriggerPx"] = request.tp_trigger_px
            if request.tp_ord_px:
                order_params["tpOrdPx"] = request.tp_ord_px
            if request.sl_trigger_px:
                order_params["slTriggerPx"] = request.sl_trigger_px
            if request.sl_ord_px:
                order_params["slOrdPx"] = request.sl_ord_px
            if request.tp_trigger_px_type:
                order_params["tpTriggerPxType"] = request.tp_trigger_px_type.value
            if request.sl_trigger_px_type:
                order_params["slTriggerPxType"] = request.sl_trigger_px_type.value

            result = self.base_service.algo_api.order_algos(**order_params)
            return self._handle_algo_response(result)

        except Exception as e:
            logger.error(f"Error placing TP/SL order: {str(e)}")
            return OKXAlgoOrderResponse(
                algo_id="",
                s_code="1",
                s_msg=str(e)
            )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=RETRY_MULTIPLIER, min=RETRY_MIN_WAIT, max=RETRY_MAX_WAIT),
        retry_error_callback=lambda retry_state: handle_retry_error(retry_state, max_retries=MAX_RETRIES)
    )
    async def place_trigger_order(self, request: OKXTriggerOrderRequest) -> OKXAlgoOrderResponse:
        """
        Place a Trigger order
        
        Args:
            request: Trigger order request
            
        Returns:
            OKXAlgoOrderResponse: Order execution result
        """
        if not await self.base_service.ensure_connected():
            return OKXAlgoOrderResponse(
                algo_id="",
                s_code="1",
                s_msg="Failed to connect to OKX API"
            )

        try:
            order_params = {
                "instId": request.inst_id,
                "tdMode": request.td_mode.value,
                "side": request.side.value,
                "ordType": request.ord_type.value,
                "sz": request.sz,
                "triggerPx": request.trigger_px,
                "triggerPxType": request.trigger_px_type.value,
                "orderPx": request.order_px,
            }
            
            if request.pos_side:
                order_params["posSide"] = request.pos_side.value
            if request.reduce_only is not None:
                order_params["reduceOnly"] = request.reduce_only
            if request.tag:
                order_params["tag"] = request.tag
            if request.cl_ord_id:
                order_params["clOrdId"] = request.cl_ord_id
            if request.attach_algo_ords:
                attach_orders = []
                for attach_order in request.attach_algo_ords:
                    attach_params = {}
                    if attach_order.attach_algo_cl_ord_id:
                        attach_params["attachAlgoClOrdId"] = attach_order.attach_algo_cl_ord_id
                    if attach_order.sl_trigger_px:
                        attach_params["slTriggerPx"] = attach_order.sl_trigger_px
                    if attach_order.sl_ord_px:
                        attach_params["slOrdPx"] = attach_order.sl_ord_px
                    if attach_order.tp_trigger_px:
                        attach_params["tpTriggerPx"] = attach_order.tp_trigger_px
                    if attach_order.tp_ord_px:
                        attach_params["tpOrdPx"] = attach_order.tp_ord_px
                    if attach_order.sl_trigger_px_type:
                        attach_params["slTriggerPxType"] = attach_order.sl_trigger_px_type.value
                    if attach_order.tp_trigger_px_type:
                        attach_params["tpTriggerPxType"] = attach_order.tp_trigger_px_type.value
                    attach_orders.append(attach_params)
                order_params["attachAlgoOrds"] = attach_orders

            result = self.base_service.algo_api.order_algos(**order_params)
            return self._handle_algo_response(result)

        except Exception as e:
            logger.error(f"Error placing trigger order: {str(e)}")
            return OKXAlgoOrderResponse(
                algo_id="",
                s_code="1",
                s_msg=str(e)
            )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=RETRY_MULTIPLIER, min=RETRY_MIN_WAIT, max=RETRY_MAX_WAIT),
        retry_error_callback=lambda retry_state: handle_retry_error(retry_state, max_retries=MAX_RETRIES)
    )
    async def place_trailing_stop_order(self, request: OKXTrailingStopRequest) -> OKXAlgoOrderResponse:
        """
        Place a Trailing Stop order
        
        Args:
            request: Trailing stop order request
            
        Returns:
            OKXAlgoOrderResponse: Order execution result
        """
        if not await self.base_service.ensure_connected():
            return OKXAlgoOrderResponse(
                algo_id="",
                s_code="1",
                s_msg="Failed to connect to OKX API"
            )

        try:
            order_params = {
                "instId": request.inst_id,
                "tdMode": request.td_mode.value,
                "side": request.side.value,
                "ordType": request.ord_type.value,
                "sz": request.sz,
                "callbackRatio": request.callback_ratio,
            }
            
            if request.pos_side:
                order_params["posSide"] = request.pos_side.value
            if request.reduce_only is not None:
                order_params["reduceOnly"] = request.reduce_only
            if request.tag:
                order_params["tag"] = request.tag
            if request.cl_ord_id:
                order_params["clOrdId"] = request.cl_ord_id
            if request.callback_spread:
                order_params["callbackSpread"] = request.callback_spread
            if request.active_px:
                order_params["activePx"] = request.active_px

            result = self.base_service.algo_api.order_algos(**order_params)
            return self._handle_algo_response(result)

        except Exception as e:
            logger.error(f"Error placing trailing stop order: {str(e)}")
            return OKXAlgoOrderResponse(
                algo_id="",
                s_code="1",
                s_msg=str(e)
            )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=RETRY_MULTIPLIER, min=RETRY_MIN_WAIT, max=RETRY_MAX_WAIT),
        retry_error_callback=lambda retry_state: handle_retry_error(retry_state, max_retries=MAX_RETRIES)
    )
    async def place_iceberg_order(self, request: OKXIcebergOrderRequest) -> OKXAlgoOrderResponse:
        """
        Place an Iceberg order
        
        Args:
            request: Iceberg order request
            
        Returns:
            OKXAlgoOrderResponse: Order execution result
        """
        if not await self.base_service.ensure_connected():
            return OKXAlgoOrderResponse(
                algo_id="",
                s_code="1",
                s_msg="Failed to connect to OKX API"
            )

        try:
            order_params = {
                "instId": request.inst_id,
                "tdMode": request.td_mode.value,
                "side": request.side.value,
                "ordType": request.ord_type.value,
                "sz": request.sz,
                "px": request.px,
                "szLimit": request.sz_limit,
                "pxVar": request.px_var,
                "pxSpread": request.px_spread,
                "szLimitType": request.sz_limit_type,
                "pxLimit": request.px_limit,
                "timeInterval": request.time_interval,
            }
            
            if request.pos_side:
                order_params["posSide"] = request.pos_side.value
            if request.reduce_only is not None:
                order_params["reduceOnly"] = request.reduce_only
            if request.tag:
                order_params["tag"] = request.tag
            if request.cl_ord_id:
                order_params["clOrdId"] = request.cl_ord_id

            result = self.base_service.algo_api.order_algos(**order_params)
            return self._handle_algo_response(result)

        except Exception as e:
            logger.error(f"Error placing iceberg order: {str(e)}")
            return OKXAlgoOrderResponse(
                algo_id="",
                s_code="1",
                s_msg=str(e)
            )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=RETRY_MULTIPLIER, min=RETRY_MIN_WAIT, max=RETRY_MAX_WAIT),
        retry_error_callback=lambda retry_state: handle_retry_error(retry_state, max_retries=MAX_RETRIES)
    )
    async def place_twap_order(self, request: OKXTWAPOrderRequest) -> OKXAlgoOrderResponse:
        """
        Place a TWAP order
        
        Args:
            request: TWAP order request
            
        Returns:
            OKXAlgoOrderResponse: Order execution result
        """
        if not await self.base_service.ensure_connected():
            return OKXAlgoOrderResponse(
                algo_id="",
                s_code="1",
                s_msg="Failed to connect to OKX API"
            )

        try:
            order_params = {
                "instId": request.inst_id,
                "tdMode": request.td_mode.value,
                "side": request.side.value,
                "ordType": request.ord_type.value,
                "sz": request.sz,
                "szLimit": request.sz_limit,
                "timeInterval": request.time_interval,
            }
            
            if request.pos_side:
                order_params["posSide"] = request.pos_side.value
            if request.reduce_only is not None:
                order_params["reduceOnly"] = request.reduce_only
            if request.tag:
                order_params["tag"] = request.tag
            if request.cl_ord_id:
                order_params["clOrdId"] = request.cl_ord_id
            if request.px_limit:
                order_params["pxLimit"] = request.px_limit
            if request.px_spread:
                order_params["pxSpread"] = request.px_spread

            result = self.base_service.algo_api.order_algos(**order_params)
            return self._handle_algo_response(result)

        except Exception as e:
            logger.error(f"Error placing TWAP order: {str(e)}")
            return OKXAlgoOrderResponse(
                algo_id="",
                s_code="1",
                s_msg=str(e)
            )

    async def cancel_algo_order(self, request: CancelAlgoOrderRequest) -> OKXAlgoOrderResponse:
        """
        Cancel an algo order
        
        Args:
            request: Cancel algo order request
            
        Returns:
            OKXAlgoOrderResponse: Cancellation result
        """
        if not await self.base_service.ensure_connected():
            return OKXAlgoOrderResponse(
                algo_id="",
                s_code="1",
                s_msg="Failed to connect to OKX API"
            )

        try:
            cancel_params = {
                "instId": request.inst_id
            }
            
            if request.algo_id:
                cancel_params["algoId"] = request.algo_id
            elif request.algo_cl_ord_id:
                cancel_params["algoClOrdId"] = request.algo_cl_ord_id
            else:
                return OKXAlgoOrderResponse(
                    algo_id="",
                    s_code="1",
                    s_msg="Either algoId or algoClOrdId must be provided"
                )

            result = self.base_service.algo_api.cancel_algos(**cancel_params)
            return self._handle_algo_response(result)

        except Exception as e:
            logger.error(f"Error canceling algo order: {str(e)}")
            return OKXAlgoOrderResponse(
                algo_id="",
                s_code="1",
                s_msg=str(e)
            )

    async def amend_algo_order(self, request: AmendAlgoOrderRequest) -> OKXAlgoOrderResponse:
        """
        Amend an algo order
        
        Args:
            request: Amend algo order request
            
        Returns:
            OKXAlgoOrderResponse: Amendment result
        """
        if not await self.base_service.ensure_connected():
            return OKXAlgoOrderResponse(
                algo_id="",
                s_code="1",
                s_msg="Failed to connect to OKX API"
            )

        try:
            amend_params = {
                "instId": request.inst_id
            }
            
            if request.algo_id:
                amend_params["algoId"] = request.algo_id
            elif request.algo_cl_ord_id:
                amend_params["algoClOrdId"] = request.algo_cl_ord_id
            else:
                return OKXAlgoOrderResponse(
                    algo_id="",
                    s_code="1",
                    s_msg="Either algoId or algoClOrdId must be provided"
                )
                
            if request.new_sz:
                amend_params["newSz"] = request.new_sz
            if request.new_tp_trigger_px:
                amend_params["newTpTriggerPx"] = request.new_tp_trigger_px
            if request.new_tp_ord_px:
                amend_params["newTpOrdPx"] = request.new_tp_ord_px
            if request.new_sl_trigger_px:
                amend_params["newSlTriggerPx"] = request.new_sl_trigger_px
            if request.new_sl_ord_px:
                amend_params["newSlOrdPx"] = request.new_sl_ord_px

            result = self.base_service.algo_api.amend_algos(**amend_params)
            return self._handle_algo_response(result)

        except Exception as e:
            logger.error(f"Error amending algo order: {str(e)}")
            return OKXAlgoOrderResponse(
                algo_id="",
                s_code="1",
                s_msg=str(e)
            )

    async def get_algo_orders(
        self, 
        ord_type: Optional[str] = None,
        algo_id: Optional[str] = None,
        inst_id: Optional[str] = None,
        state: Optional[str] = None,
        limit: str = "100"
    ) -> List[OKXAlgoOrder]:
        """
        Get algo orders list
        
        Args:
            ord_type: Order type filter
            algo_id: Algo order ID filter
            inst_id: Instrument ID filter
            state: Order state filter
            limit: Number of results to return
            
        Returns:
            List[OKXAlgoOrder]: List of algo orders
        """
        if not await self.base_service.ensure_connected():
            return []

        try:
            params = {
                "limit": limit
            }
            
            if ord_type:
                params["ordType"] = ord_type
            if algo_id:
                params["algoId"] = algo_id
            if inst_id:
                params["instId"] = inst_id
            if state:
                params["state"] = state

            result = self.base_service.algo_api.order_algos_list(**params)
            
            if not result or 'data' not in result:
                return []

            orders = []
            for order_data in result['data']:
                try:
                    order = OKXAlgoOrder(**order_data)
                    orders.append(order)
                except Exception as e:
                    logger.warning(f"Failed to parse algo order data: {e}")
                    continue
                    
            return orders

        except Exception as e:
            logger.error(f"Error getting algo orders: {str(e)}")
            return []

    async def get_algo_order_details(
        self, 
        algo_id: Optional[str] = None,
        algo_cl_ord_id: Optional[str] = None
    ) -> Optional[OKXAlgoOrder]:
        """
        Get algo order details
        
        Args:
            algo_id: Algo order ID
            algo_cl_ord_id: Client algo order ID
            
        Returns:
            Optional[OKXAlgoOrder]: Algo order details if found
        """
        if not await self.base_service.ensure_connected():
            return None

        try:
            params = {}
            
            if algo_id:
                params["algoId"] = algo_id
            elif algo_cl_ord_id:
                params["algoClOrdId"] = algo_cl_ord_id
            else:
                return None

            result = self.base_service.algo_api.order_algo(**params)
            
            if not result or 'data' not in result or not result['data']:
                return None

            order_data = result['data'][0]
            return OKXAlgoOrder(**order_data)

        except Exception as e:
            logger.error(f"Error getting algo order details: {str(e)}")
            return None

    def _handle_algo_response(self, result: Dict[str, Any]) -> OKXAlgoOrderResponse:
        """
        Handle OKX algo API response
        
        Args:
            result: API response
            
        Returns:
            OKXAlgoOrderResponse: Formatted response
        """
        if not result or 'data' not in result or not result['data']:
            error_msg = result.get('msg', 'Unknown error') if result else 'No response'
            logger.error(f"Algo order failed: {error_msg}")
            return OKXAlgoOrderResponse(
                algo_id="",
                s_code="1",
                s_msg=f"Algo order failed: {error_msg}"
            )

        order_data = result['data'][0]
        
        if order_data['sCode'] != '0':
            logger.error(f"Algo order failed: {order_data['sMsg']}")
            return OKXAlgoOrderResponse(
                algo_id=order_data.get('algoId', ''),
                algo_cl_ord_id=order_data.get('algoClOrdId'),
                s_code=order_data['sCode'],
                s_msg=order_data['sMsg']
            )

        logger.info(f"Algo order placed successfully: Algo ID {order_data['algoId']}")
        return OKXAlgoOrderResponse(
            algo_id=order_data['algoId'],
            algo_cl_ord_id=order_data.get('algoClOrdId'),
            s_code=order_data['sCode'],
            s_msg=order_data['sMsg']
        )