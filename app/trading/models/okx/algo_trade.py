from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum
from .trade import OrderSide, TradeMode, PositionSide

class AlgoOrderType(str, Enum):
    CONDITIONAL = "conditional"  # TP/SL
    TRIGGER = "trigger"
    MOVE_ORDER_STOP = "move_order_stop"  # Trailing stop
    ICEBERG = "iceberg"
    TWAP = "twap"

class TriggerPriceType(str, Enum):
    LAST = "last"
    INDEX = "index"
    MARK = "mark"

class AlgoOrderState(str, Enum):
    LIVE = "live"
    PAUSE = "pause"
    EFFECTIVE = "effective"
    CANCELED = "canceled"
    ORDER_FAILED = "order_failed"

class AttachAlgoOrder(BaseModel):
    """Attached algo order for stop loss and take profit"""
    attach_algo_cl_ord_id: Optional[str] = Field(None, description="Client order ID for attached algo order")
    sl_trigger_px: Optional[str] = Field(None, description="Stop loss trigger price")
    sl_ord_px: Optional[str] = Field(None, description="Stop loss order price")
    tp_trigger_px: Optional[str] = Field(None, description="Take profit trigger price")
    tp_ord_px: Optional[str] = Field(None, description="Take profit order price")
    sl_trigger_px_type: Optional[TriggerPriceType] = Field(None, description="Stop loss trigger price type")
    tp_trigger_px_type: Optional[TriggerPriceType] = Field(None, description="Take profit trigger price type")

class OKXAlgoOrderRequest(BaseModel):
    """Base request model for OKX algo trading orders"""
    inst_id: str = Field(..., description="Instrument ID")
    td_mode: TradeMode = Field(..., description="Trade mode")
    side: OrderSide = Field(..., description="Order side")
    ord_type: AlgoOrderType = Field(..., description="Algo order type")
    sz: str = Field(..., description="Quantity to buy or sell")
    pos_side: Optional[PositionSide] = Field(None, description="Position side")
    reduce_only: Optional[bool] = Field(None, description="Whether order is reduce-only")
    tag: Optional[str] = Field(None, description="Order tag")
    cl_ord_id: Optional[str] = Field(None, description="Client order ID")
    
class OKXTPSLOrderRequest(OKXAlgoOrderRequest):
    """Take Profit / Stop Loss order request"""
    ord_type: AlgoOrderType = Field(default=AlgoOrderType.CONDITIONAL)
    tp_trigger_px: Optional[str] = Field(None, description="Take profit trigger price")
    tp_ord_px: Optional[str] = Field(None, description="Take profit order price")
    sl_trigger_px: Optional[str] = Field(None, description="Stop loss trigger price") 
    sl_ord_px: Optional[str] = Field(None, description="Stop loss order price")
    tp_trigger_px_type: Optional[TriggerPriceType] = Field(None, description="Take profit trigger price type")
    sl_trigger_px_type: Optional[TriggerPriceType] = Field(None, description="Stop loss trigger price type")

class OKXTriggerOrderRequest(OKXAlgoOrderRequest):
    """Trigger order request"""
    ord_type: AlgoOrderType = Field(default=AlgoOrderType.TRIGGER)
    trigger_px: str = Field(..., description="Trigger price")
    trigger_px_type: TriggerPriceType = Field(default=TriggerPriceType.LAST, description="Trigger price type")
    order_px: str = Field(..., description="Order price")
    attach_algo_ords: Optional[List[AttachAlgoOrder]] = Field(None, description="Attached algo orders")

class OKXTrailingStopRequest(OKXAlgoOrderRequest):
    """Trailing stop order request"""
    ord_type: AlgoOrderType = Field(default=AlgoOrderType.MOVE_ORDER_STOP)
    callback_ratio: str = Field(..., description="Callback ratio (e.g., '0.05' for 5%)")
    callback_spread: Optional[str] = Field(None, description="Callback spread")
    active_px: Optional[str] = Field(None, description="Activation price")

class OKXIcebergOrderRequest(OKXAlgoOrderRequest):
    """Iceberg order request"""
    ord_type: AlgoOrderType = Field(default=AlgoOrderType.ICEBERG)
    px: str = Field(..., description="Order price")
    sz_limit: str = Field(..., description="Single order size")
    px_var: str = Field(..., description="Price variance")
    px_spread: str = Field(..., description="Price spread")
    sz_limit_type: str = Field(default="base_ccy", description="Size limit type")
    px_limit: str = Field(..., description="Price limit")
    time_interval: str = Field(..., description="Time interval")

class OKXTWAPOrderRequest(OKXAlgoOrderRequest):
    """TWAP order request"""
    ord_type: AlgoOrderType = Field(default=AlgoOrderType.TWAP)
    sz_limit: str = Field(..., description="Single order size")
    px_limit: Optional[str] = Field(None, description="Price limit")
    time_interval: str = Field(..., description="Time interval")
    px_spread: Optional[str] = Field(None, description="Price spread")

class OKXAlgoOrderResponse(BaseModel):
    """Response model for algo order operations"""
    algo_id: str = Field(..., description="Algo order ID")
    algo_cl_ord_id: Optional[str] = Field(None, description="Client algo order ID")
    s_code: str = Field(..., description="Error code")
    s_msg: str = Field(..., description="Error message")
    
    @property
    def success(self) -> bool:
        return self.s_code == "0"

class OKXAlgoOrder(BaseModel):
    """Algo order details model"""
    algo_id: str = Field(..., alias="algoId", description="Algo order ID")
    algo_cl_ord_id: Optional[str] = Field(None, alias="algoClOrdId", description="Client algo order ID")
    inst_id: str = Field(..., alias="instId", description="Instrument ID")
    ord_type: str = Field(..., alias="ordType", description="Order type")
    side: str = Field(..., description="Order side")
    pos_side: Optional[str] = Field(None, alias="posSide", description="Position side")
    td_mode: str = Field(..., alias="tdMode", description="Trade mode")
    sz: str = Field(..., description="Order size")
    state: str = Field(..., description="Algo order state")
    lever: Optional[str] = Field(None, description="Leverage")
    tp_trigger_px: Optional[str] = Field(None, alias="tpTriggerPx", description="Take profit trigger price")
    tp_ord_px: Optional[str] = Field(None, alias="tpOrdPx", description="Take profit order price")
    sl_trigger_px: Optional[str] = Field(None, alias="slTriggerPx", description="Stop loss trigger price")
    sl_ord_px: Optional[str] = Field(None, alias="slOrdPx", description="Stop loss order price")
    trigger_px: Optional[str] = Field(None, alias="triggerPx", description="Trigger price")
    order_px: Optional[str] = Field(None, alias="orderPx", description="Order price")
    callback_ratio: Optional[str] = Field(None, alias="callbackRatio", description="Callback ratio")
    callback_spread: Optional[str] = Field(None, alias="callbackSpread", description="Callback spread")
    active_px: Optional[str] = Field(None, alias="activePx", description="Activation price")
    px: Optional[str] = Field(None, description="Price")
    px_var: Optional[str] = Field(None, alias="pxVar", description="Price variance")
    px_spread: Optional[str] = Field(None, alias="pxSpread", description="Price spread")
    sz_limit: Optional[str] = Field(None, alias="szLimit", description="Size limit")
    px_limit: Optional[str] = Field(None, alias="pxLimit", description="Price limit")
    time_interval: Optional[str] = Field(None, alias="timeInterval", description="Time interval")
    count: Optional[str] = Field(None, description="Count")
    ord_id_list: Optional[List[str]] = Field(None, alias="ordIdList", description="Order ID list")
    reduce_only: Optional[str] = Field(None, alias="reduceOnly", description="Reduce only")
    tag: Optional[str] = Field(None, description="Order tag")
    actual_sz: Optional[str] = Field(None, alias="actualSz", description="Actual size")
    actual_px: Optional[str] = Field(None, alias="actualPx", description="Actual price")
    actual_side: Optional[str] = Field(None, alias="actualSide", description="Actual side")
    pnl: Optional[str] = Field(None, description="P&L")
    c_time: str = Field(..., alias="cTime", description="Creation time")
    trigger_time: Optional[str] = Field(None, alias="triggerTime", description="Trigger time")
    u_time: Optional[str] = Field(None, alias="uTime", description="Update time")
    
    model_config = {"populate_by_name": True}

class CancelAlgoOrderRequest(BaseModel):
    """Cancel algo order request"""
    algo_id: Optional[str] = Field(None, description="Algo order ID")
    algo_cl_ord_id: Optional[str] = Field(None, description="Client algo order ID")
    inst_id: str = Field(..., description="Instrument ID")

class AmendAlgoOrderRequest(BaseModel):
    """Amend algo order request"""
    algo_id: Optional[str] = Field(None, description="Algo order ID") 
    algo_cl_ord_id: Optional[str] = Field(None, description="Client algo order ID")
    inst_id: str = Field(..., description="Instrument ID")
    new_sz: Optional[str] = Field(None, description="New size")
    new_tp_trigger_px: Optional[str] = Field(None, description="New take profit trigger price")
    new_tp_ord_px: Optional[str] = Field(None, description="New take profit order price")
    new_sl_trigger_px: Optional[str] = Field(None, description="New stop loss trigger price")
    new_sl_ord_px: Optional[str] = Field(None, description="New stop loss order price")