from fastapi import APIRouter, HTTPException, Depends
from app.trading_app.services.okx.okx_algo_service import OKXAlgoService
from app.trading_app.models.okx.algo_trade import (
    OKXTPSLOrderRequest, OKXTriggerOrderRequest, OKXTrailingStopRequest,
    OKXIcebergOrderRequest, OKXTWAPOrderRequest, OKXAlgoOrderResponse,
    CancelAlgoOrderRequest, AmendAlgoOrderRequest
)
from typing import List, Optional

def get_router(algo_service: OKXAlgoService) -> APIRouter:
    router = APIRouter(prefix="/algo-trading", tags=["OKX Algo Trading"])

    @router.post("/place-tp-sl",
        response_model=OKXAlgoOrderResponse,
        summary="Place Take Profit / Stop Loss Order",
        description="Place a take profit and/or stop loss algo order")
    async def place_tp_sl_order(request: OKXTPSLOrderRequest):
        """
        Place a Take Profit / Stop Loss order
        
        This endpoint allows you to place conditional orders with take profit and/or stop loss triggers:
        
        **Order Parameters:**
        - **inst_id**: Instrument ID (required)
        - **td_mode**: Trading mode (cash/cross/isolated)
        - **side**: Order side (buy/sell)
        - **sz**: Order size
        - **tp_trigger_px**: Take profit trigger price
        - **tp_ord_px**: Take profit order price (-1 for market price)
        - **sl_trigger_px**: Stop loss trigger price
        - **sl_ord_px**: Stop loss order price (-1 for market price)
        
        **Trigger Price Types:**
        - **last**: Last traded price
        - **index**: Index price
        - **mark**: Mark price
        
        **Examples:**
        - TP/SL for long position: `{"inst_id": "BTC-USDT", "td_mode": "cross", "side": "buy", "sz": "2", "tp_trigger_px": "15", "tp_ord_px": "18"}`
        - Stop loss only: `{"inst_id": "ETH-USDT", "td_mode": "cash", "side": "sell", "sz": "0.1", "sl_trigger_px": "1800", "sl_ord_px": "-1"}`
        """
        try:
            result = await algo_service.place_tp_sl_order(request)
            
            if not result.success:
                raise HTTPException(status_code=400, detail=result.s_msg)
                
            return result
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/place-trigger",
        response_model=OKXAlgoOrderResponse,
        summary="Place Trigger Order",
        description="Place a trigger order with optional attached TP/SL")
    async def place_trigger_order(request: OKXTriggerOrderRequest):
        """
        Place a Trigger order
        
        This endpoint places an order that executes when price reaches the trigger level:
        
        **Order Parameters:**
        - **inst_id**: Instrument ID (required)
        - **td_mode**: Trading mode (cash/cross/isolated)
        - **side**: Order side (buy/sell)
        - **sz**: Order size
        - **trigger_px**: Trigger price
        - **trigger_px_type**: Trigger price type (last/index/mark)
        - **order_px**: Order price (-1 for market price)
        - **attach_algo_ords**: Optional attached TP/SL orders
        
        **Attached Algo Orders:**
        Can include stop loss and take profit orders that activate after the main order fills
        
        **Examples:**
        - Basic trigger: `{"inst_id": "BTC-USDT-SWAP", "side": "buy", "td_mode": "cross", "sz": "1", "trigger_px": "25920", "order_px": "-1"}`
        - With TP/SL: Include `attach_algo_ords` array with TP/SL parameters
        """
        try:
            result = await algo_service.place_trigger_order(request)
            
            if not result.success:
                raise HTTPException(status_code=400, detail=result.s_msg)
                
            return result
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/place-trailing-stop",
        response_model=OKXAlgoOrderResponse,
        summary="Place Trailing Stop Order",
        description="Place a trailing stop order")
    async def place_trailing_stop_order(request: OKXTrailingStopRequest):
        """
        Place a Trailing Stop order
        
        This endpoint places a trailing stop order that adjusts the stop price as the market moves favorably:
        
        **Order Parameters:**
        - **inst_id**: Instrument ID (required)
        - **td_mode**: Trading mode (cross/isolated)
        - **side**: Order side (buy/sell)
        - **sz**: Order size
        - **callback_ratio**: Callback ratio (e.g., "0.05" for 5%)
        - **callback_spread**: Optional callback spread
        - **active_px**: Optional activation price
        - **reduce_only**: Must be true for closing positions
        
        **How it works:**
        - For sell orders: Stop price trails below the highest price by callback_ratio
        - For buy orders: Stop price trails above the lowest price by callback_ratio
        
        **Examples:**
        - Basic trailing stop: `{"inst_id": "BTC-USDT-SWAP", "td_mode": "cross", "side": "buy", "sz": "10", "callback_ratio": "0.05", "reduce_only": true}`
        """
        try:
            result = await algo_service.place_trailing_stop_order(request)
            
            if not result.success:
                raise HTTPException(status_code=400, detail=result.s_msg)
                
            return result
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/place-iceberg",
        response_model=OKXAlgoOrderResponse,
        summary="Place Iceberg Order",
        description="Place an iceberg order to hide large order sizes")
    async def place_iceberg_order(request: OKXIcebergOrderRequest):
        """
        Place an Iceberg order
        
        This endpoint places large orders in smaller chunks to reduce market impact:
        
        **Order Parameters:**
        - **inst_id**: Instrument ID (required)
        - **td_mode**: Trading mode (cash/cross/isolated)
        - **side**: Order side (buy/sell)
        - **sz**: Total order size
        - **px**: Order price
        - **sz_limit**: Size of each individual order
        - **px_var**: Price variance
        - **px_spread**: Price spread
        - **px_limit**: Price limit
        - **time_interval**: Time interval between orders
        
        **How it works:**
        - Splits large order into smaller chunks (sz_limit)
        - Places orders at intervals with price variation
        - Helps hide trading intentions from market
        
        **Examples:**
        - Large buy order: Split 100 BTC into 10 BTC chunks with price variance
        """
        try:
            result = await algo_service.place_iceberg_order(request)
            
            if not result.success:
                raise HTTPException(status_code=400, detail=result.s_msg)
                
            return result
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/place-twap",
        response_model=OKXAlgoOrderResponse,
        summary="Place TWAP Order",
        description="Place a Time-Weighted Average Price order")
    async def place_twap_order(request: OKXTWAPOrderRequest):
        """
        Place a TWAP (Time-Weighted Average Price) order
        
        This endpoint places orders that execute over time to achieve average pricing:
        
        **Order Parameters:**
        - **inst_id**: Instrument ID (required)
        - **td_mode**: Trading mode (cash/cross/isolated)
        - **side**: Order side (buy/sell)
        - **sz**: Total order size
        - **sz_limit**: Size of each individual order
        - **time_interval**: Time interval between orders (seconds)
        - **px_limit**: Optional price limit
        - **px_spread**: Optional price spread
        
        **How it works:**
        - Splits total size into smaller orders
        - Executes orders at regular intervals
        - Aims to achieve time-weighted average price
        - Reduces market impact of large orders
        
        **Examples:**
        - TWAP buy: `{"inst_id": "BTC-USDT-SWAP", "td_mode": "cross", "side": "buy", "sz": "10", "sz_limit": "1", "time_interval": "60"}`
        - With price limit: Include `px_limit` to set maximum/minimum price
        """
        try:
            result = await algo_service.place_twap_order(request)
            
            if not result.success:
                raise HTTPException(status_code=400, detail=result.s_msg)
                
            return result
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/cancel-order",
        response_model=OKXAlgoOrderResponse,
        summary="Cancel Algo Order",
        description="Cancel an existing algo order")
    async def cancel_algo_order(request: CancelAlgoOrderRequest):
        """
        Cancel an algo order
        
        This endpoint cancels pending algo orders:
        
        **Request Parameters:**
        - **inst_id**: Instrument ID (required)
        - **algo_id**: Algo order ID (either this or algo_cl_ord_id required)
        - **algo_cl_ord_id**: Client algo order ID (either this or algo_id required)
        
        **Cancellable States:**
        - **live**: Order is active and waiting for trigger
        - **pause**: Order is paused
        - **effective**: Order is effective (for some order types)
        
        **Cannot cancel:**
        - **canceled**: Already canceled
        - **order_failed**: Failed orders
        - Orders that have already been triggered
        
        **Examples:**
        - By algo ID: `{"inst_id": "BTC-USDT", "algo_id": "12345"}`
        - By client ID: `{"inst_id": "ETH-USDT", "algo_cl_ord_id": "my_algo_001"}`
        """
        try:
            result = await algo_service.cancel_algo_order(request)
            
            if not result.success:
                raise HTTPException(status_code=400, detail=result.s_msg)
                
            return result
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/amend-order",
        response_model=OKXAlgoOrderResponse,
        summary="Amend Algo Order",
        description="Modify an existing algo order")
    async def amend_algo_order(request: AmendAlgoOrderRequest):
        """
        Amend an algo order
        
        This endpoint modifies parameters of existing algo orders:
        
        **Request Parameters:**
        - **inst_id**: Instrument ID (required)
        - **algo_id**: Algo order ID (either this or algo_cl_ord_id required)
        - **algo_cl_ord_id**: Client algo order ID (either this or algo_id required)
        - **new_sz**: New order size
        - **new_tp_trigger_px**: New take profit trigger price
        - **new_tp_ord_px**: New take profit order price
        - **new_sl_trigger_px**: New stop loss trigger price
        - **new_sl_ord_px**: New stop loss order price
        
        **Amendable Parameters:**
        - Order size (for most order types)
        - Take profit/stop loss trigger and order prices
        - Some order-specific parameters
        
        **Amendable States:**
        - **live**: Active orders waiting for trigger
        - **pause**: Paused orders (for some types)
        
        **Examples:**
        - Change size: `{"inst_id": "BTC-USDT", "algo_id": "12345", "new_sz": "5"}`
        - Update TP: `{"inst_id": "ETH-USDT", "algo_id": "67890", "new_tp_trigger_px": "2100"}`
        """
        try:
            result = await algo_service.amend_algo_order(request)
            
            if not result.success:
                raise HTTPException(status_code=400, detail=result.s_msg)
                
            return result
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/orders",
        summary="Get Algo Orders",
        description="Get list of algo orders with optional filters")
    async def get_algo_orders(
        ord_type: Optional[str] = None,
        algo_id: Optional[str] = None,
        inst_id: Optional[str] = None,
        state: Optional[str] = None,
        limit: str = "100"
    ):
        """
        Get algo orders list
        
        This endpoint retrieves algo orders with filtering options:
        
        **Query Parameters:**
        - **ord_type**: Filter by order type
          - **conditional**: TP/SL orders
          - **trigger**: Trigger orders
          - **move_order_stop**: Trailing stop orders
          - **iceberg**: Iceberg orders
          - **twap**: TWAP orders
        - **algo_id**: Filter by specific algo order ID
        - **inst_id**: Filter by instrument (e.g., "BTC-USDT")
        - **state**: Filter by order state
          - **live**: Active orders
          - **pause**: Paused orders
          - **effective**: Effective orders
          - **canceled**: Canceled orders
          - **order_failed**: Failed orders
        - **limit**: Number of results (max 100, default 100)
        
        **Examples:**
        - All trigger orders: `?ord_type=trigger`
        - BTC orders: `?inst_id=BTC-USDT`
        - Active orders: `?state=live`
        - Recent 50 orders: `?limit=50`
        """
        try:
            orders = await algo_service.get_algo_orders(
                ord_type=ord_type,
                algo_id=algo_id,
                inst_id=inst_id,
                state=state,
                limit=limit
            )
            
            return {
                "status": "success",
                "data": orders,
                "count": len(orders)
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/order/details",
        summary="Get Algo Order Details",
        description="Get detailed information of a specific algo order")
    async def get_algo_order_details(
        algo_id: Optional[str] = None,
        algo_cl_ord_id: Optional[str] = None
    ):
        """
        Get detailed information of a specific algo order
        
        This endpoint retrieves comprehensive details of a single algo order:
        
        **Query Parameters:**
        - **algo_id**: Platform-assigned algo order ID
        - **algo_cl_ord_id**: Your custom client algo order ID
        
        **Note**: Either `algo_id` OR `algo_cl_ord_id` must be provided
        
        **Response includes:**
        - Order parameters and current state
        - Trigger conditions and prices
        - Execution history and statistics
        - Associated order IDs if triggered
        - Timestamps and performance metrics
        
        **Examples:**
        - By algo ID: `?algo_id=12345`
        - By client ID: `?algo_cl_ord_id=my_algo_001`
        """
        if not algo_id and not algo_cl_ord_id:
            raise HTTPException(
                status_code=400,
                detail="Either algo_id or algo_cl_ord_id must be provided"
            )
            
        try:
            order = await algo_service.get_algo_order_details(
                algo_id=algo_id,
                algo_cl_ord_id=algo_cl_ord_id
            )
            
            if not order:
                raise HTTPException(status_code=404, detail="Algo order not found")
                
            return {
                "status": "success",
                "data": order
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return router