from fastapi import APIRouter, HTTPException, Depends
from app.trading.services.okx.okx_trading_service import OKXTradingService
from app.trading.models.okx.trade import OKXTradeRequest, OKXTradeResponse, CancelOKXOrderRequest, ModifyOKXOrderRequest, CloseOKXPositionRequest, CloseOKXPositionResponse
from typing import List, Optional
from shared.service_registry import get_services

router = APIRouter(prefix="/okx/trading", tags=["OKX Trading"])

def get_trading_service() -> OKXTradingService:
    services = get_services()
    return services.okx_trading_service

@router.post("/place-order",
    response_model=OKXTradeResponse,
    summary="Place Order",
    description="Place a new trading order on OKX")
async def place_order(
    trade_request: OKXTradeRequest,
    trading_service: OKXTradingService = Depends(get_trading_service)
):
    try:
        result = await trading_service.place_order(trade_request)

        if not result.success:
            raise HTTPException(status_code=400, detail=result.s_msg)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cancel-order",
    response_model=OKXTradeResponse,
    summary="Cancel Order",
    description="Cancel an existing order")
async def cancel_order(
    cancel_request: CancelOKXOrderRequest,
    trading_service: OKXTradingService = Depends(get_trading_service)
):
    try:
        result = await trading_service.cancel_order(cancel_request)

        if not result.success:
            raise HTTPException(status_code=400, detail=result.s_msg)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/modify-order",
    response_model=OKXTradeResponse,
    summary="Modify Order",
    description="Modify an existing order")
async def modify_order(
    modify_request: ModifyOKXOrderRequest,
    trading_service: OKXTradingService = Depends(get_trading_service)
):
    try:
        result = await trading_service.modify_order(modify_request)

        if not result.success:
            raise HTTPException(status_code=400, detail=result.s_msg)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/orders",
    summary="Get Orders",
    description="Get order history")
async def get_orders(
    inst_id: Optional[str] = None,
    inst_type: str = "SPOT",
    state: Optional[str] = None,
    limit: str = "100",
    trading_service: OKXTradingService = Depends(get_trading_service)
):
    try:
        orders = await trading_service.get_orders(
            inst_id=inst_id,
            ult_type=inst_type,
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

@router.get("/order/{inst_id}",
    summary="Get Order Details",
    description="Get details of a specific order")
async def get_order_details(
    inst_id: str,
    ord_id: Optional[str] = None,
    cl_ord_id: Optional[str] = None,
    trading_service: OKXTradingService = Depends(get_trading_service)
):
    if not ord_id and not cl_ord_id:
        raise HTTPException(
            status_code=400,
            detail="Either ord_id or cl_ord_id must be provided"
        )

    try:
        order = await trading_service.get_order_details(
            inst_id=inst_id,
            ord_id=ord_id,
            cl_ord_id=cl_ord_id
        )

        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        return {
            "status": "success",
            "data": order
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/close-position",
    response_model=CloseOKXPositionResponse,
    summary="Close Position",
    description="Close position using market order")
async def close_position(
    close_request: CloseOKXPositionRequest,
    trading_service: OKXTradingService = Depends(get_trading_service)
):
    result = await trading_service.close_position(close_request)
    return result