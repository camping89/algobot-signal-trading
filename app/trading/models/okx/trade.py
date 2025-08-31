from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from enum import Enum
from decimal import Decimal
from datetime import datetime

class OrderType(str, Enum):
    BUY = "buy"
    SELL = "sell"

class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"

class TradeMode(str, Enum):
    CASH = "cash"
    CROSS = "cross" 
    ISOLATED = "isolated"

class PositionSide(str, Enum):
    LONG = "long"
    SHORT = "short"
    NET = "net"

class OKXPosition(BaseModel):
    inst_id: str = Field(..., description="Instrument ID")
    pos_id: str = Field(..., description="Position ID")
    trade_id: str = Field(..., description="Trade ID")
    pos_side: PositionSide = Field(..., description="Position side")
    pos: Decimal = Field(..., description="Position size")
    avg_px: Decimal = Field(..., description="Average position price")
    upl: Decimal = Field(..., description="Unrealized P&L")
    upl_ratio: Optional[Decimal] = Field(None, description="Unrealized P&L ratio")
    notional_usd: Decimal = Field(..., description="Notional value in USD")
    adl: str = Field(..., description="Auto-deleveraging indicator")
    margin: Decimal = Field(..., description="Margin")
    margin_ratio: Optional[Decimal] = Field(None, description="Margin ratio")
    mm_r: Decimal = Field(..., description="Maintenance margin ratio")
    lever: str = Field(..., description="Leverage")
    last_px: Decimal = Field(..., description="Last price")
    mark_px: Decimal = Field(..., description="Mark price")
    u_time: str = Field(..., description="Update time")
    c_time: str = Field(..., description="Creation time")

class OKXAccountInfo(BaseModel):
    total_eq: Decimal = Field(..., description="Total equity")
    adj_eq: Optional[Decimal] = Field(None, description="Adjusted equity")
    iso_eq: Decimal = Field(..., description="Isolated margin equity")
    ord_froz: Decimal = Field(..., description="Margin frozen for pending orders")
    imr: Decimal = Field(..., description="Initial margin requirement")
    mmr: Decimal = Field(..., description="Maintenance margin requirement")
    notional_usd: Decimal = Field(..., description="Notional value in USD")
    u_time: str = Field(..., description="Update time")

class OKXTradeRequest(BaseModel):
    inst_id: str = Field(
        ..., 
        description="Instrument ID (e.g., BTC-USDT, ETH-USDT)"
    )
    td_mode: TradeMode = Field(
        default=TradeMode.CASH,
        description="Trade mode: cash, cross, isolated"
    )
    side: OrderSide = Field(
        ..., 
        description="Order side: buy or sell"
    )
    ord_type: str = Field(
        default="market",
        description="Order type: market, limit, post_only, fok, ioc"
    )
    sz: str = Field(
        ..., 
        description="Quantity to buy or sell"
    )
    px: Optional[str] = Field(
        None, 
        description="Order price for limit orders"
    )
    ccy: Optional[str] = Field(
        None,
        description="Currency for margin trading"
    )
    cl_ord_id: Optional[str] = Field(
        None,
        description="Client order ID"
    )
    tag: Optional[str] = Field(
        None, 
        description="Order tag"
    )
    pos_side: Optional[PositionSide] = Field(
        None,
        description="Position side for futures/swap"
    )
    reduce_only: Optional[bool] = Field(
        None,
        description="Whether the order is reduce-only"
    )
    tp_trigger_px: Optional[str] = Field(
        None,
        description="Take profit trigger price"
    )
    tp_ord_px: Optional[str] = Field(
        None,
        description="Take profit order price"
    )
    sl_trigger_px: Optional[str] = Field(
        None,
        description="Stop loss trigger price"
    )
    sl_ord_px: Optional[str] = Field(
        None,
        description="Stop loss order price"
    )
    tp_trigger_px_type: Optional[str] = Field(
        None,
        description="Take profit trigger price type: last, index, mark"
    )
    sl_trigger_px_type: Optional[str] = Field(
        None,
        description="Stop loss trigger price type: last, index, mark"
    )
    quick_margin_type: Optional[str] = Field(
        None,
        description="Quick margin type: manual, auto_borrow, auto_repay"
    )
    stp_id: Optional[str] = Field(
        None,
        description="Self trade prevention ID"
    )
    stp_mode: Optional[str] = Field(
        None,
        description="Self trade prevention mode: cancel_maker, cancel_taker, cancel_both"
    )
    banner_flag: Optional[str] = Field(
        None,
        description="Banner flag for special order marking"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "inst_id": "BTC-USDT",
                "td_mode": "cash",
                "side": "buy",
                "ord_type": "market",
                "sz": "0.001",
                "tag": "python_bot"
            }
        }

class OKXTradeResponse(BaseModel):
    ord_id: str = Field(..., description="Order ID")
    cl_ord_id: Optional[str] = Field(None, description="Client order ID")
    tag: Optional[str] = Field(None, description="Order tag")
    s_code: str = Field(..., description="Error code")
    s_msg: str = Field(..., description="Error message")
    
    @property
    def success(self) -> bool:
        return self.s_code == "0"

class OKXOrder(BaseModel):
    inst_id: str = Field(..., alias="instId", description="Instrument ID")
    ord_id: str = Field(..., alias="ordId", description="Order ID")
    cl_ord_id: Optional[str] = Field(None, alias="clOrdId", description="Client order ID")
    tag: Optional[str] = Field(None, description="Order tag")
    px: str = Field(..., description="Order price")
    sz: str = Field(..., description="Order size")
    ord_type: str = Field(..., alias="ordType", description="Order type")
    side: str = Field(..., description="Order side")
    pos_side: Optional[str] = Field(None, alias="posSide", description="Position side")
    td_mode: str = Field(..., alias="tdMode", description="Trade mode")
    acc_fill_sz: str = Field(..., alias="accFillSz", description="Accumulated fill quantity")
    fill_px: str = Field(..., alias="fillPx", description="Last filled price")
    trade_id: str = Field(..., alias="tradeId", description="Last trade ID")
    fill_sz: str = Field(..., alias="fillSz", description="Last fill quantity")
    fill_time: str = Field(..., alias="fillTime", description="Last fill time")
    state: str = Field(..., description="Order state")
    avg_px: str = Field(..., alias="avgPx", description="Average filled price")
    lever: str = Field(..., description="Leverage")
    tp_trigger_px: Optional[str] = Field(None, alias="tpTriggerPx", description="Take profit trigger price")
    tp_ord_px: Optional[str] = Field(None, alias="tpOrdPx", description="Take profit order price")
    sl_trigger_px: Optional[str] = Field(None, alias="slTriggerPx", description="Stop loss trigger price")
    sl_ord_px: Optional[str] = Field(None, alias="slOrdPx", description="Stop loss order price")
    fee_ccy: str = Field(..., alias="feeCcy", description="Fee currency")
    fee: str = Field(..., description="Fee")
    rebate_ccy: str = Field(..., alias="rebateCcy", description="Rebate currency")
    rebate: str = Field(..., description="Rebate")
    pnl: str = Field(..., description="P&L")
    source: str = Field(..., description="Order source")
    category: str = Field(..., description="Order category")
    u_time: str = Field(..., alias="uTime", description="Update time")
    c_time: str = Field(..., alias="cTime", description="Creation time")
    
    model_config = {"populate_by_name": True}

class OKXBalance(BaseModel):
    ccy: str = Field(..., description="Currency")
    bal: str = Field(..., description="Balance")
    frozen_bal: str = Field(..., description="Frozen balance")
    avail_bal: str = Field(..., description="Available balance")

class OKXTicker(BaseModel):
    inst_id: str = Field(..., description="Instrument ID")
    last: str = Field(..., description="Last traded price")
    last_sz: str = Field(..., description="Last traded size")
    ask_px: str = Field(..., description="Best ask price")
    ask_sz: str = Field(..., description="Best ask size")
    bid_px: str = Field(..., description="Best bid price")
    bid_sz: str = Field(..., description="Best bid size")
    open_24h: str = Field(..., description="24h opening price")
    high_24h: str = Field(..., description="24h highest price")
    low_24h: str = Field(..., description="24h lowest price")
    vol_24h: str = Field(..., description="24h trading volume")
    vol_ccy_24h: str = Field(..., description="24h trading volume in quote currency")
    sod_utc0: str = Field(..., description="Start of day price (UTC+0)")
    sod_utc8: str = Field(..., description="Start of day price (UTC+8)")
    ts: str = Field(..., description="Ticker data timestamp")

class OKXInstrument(BaseModel):
    inst_id: str = Field(..., description="Instrument ID")
    uly: Optional[str] = Field(None, description="Underlying")
    inst_type: str = Field(..., description="Instrument type")
    base_ccy: str = Field(..., description="Base currency")
    quote_ccy: str = Field(..., description="Quote currency")
    settle_ccy: str = Field(..., description="Settlement currency")
    ct_val: str = Field(..., description="Contract value")
    ct_mult: str = Field(..., description="Contract multiplier")
    ct_val_ccy: str = Field(..., description="Contract value currency")
    opt_type: Optional[str] = Field(None, description="Option type")
    stk: Optional[str] = Field(None, description="Strike price")
    list_time: str = Field(..., description="Listing time")
    exp_time: Optional[str] = Field(None, description="Expiry time")
    lever: str = Field(..., description="Max leverage")
    tick_sz: str = Field(..., description="Tick size")
    lot_sz: str = Field(..., description="Lot size")
    min_sz: str = Field(..., description="Minimum order size")
    ct_type: Optional[str] = Field(None, description="Contract type")
    alias: Optional[str] = Field(None, description="Alias")
    state: str = Field(..., description="Instrument state")

class OKXHistoricalTrade(BaseModel):
    inst_id: str = Field(..., description="Instrument ID")
    ord_id: str = Field(..., description="Order ID")
    trade_id: str = Field(..., description="Trade ID")
    fill_px: str = Field(..., description="Fill price")
    fill_sz: str = Field(..., description="Fill size")
    side: str = Field(..., description="Order side")
    fee: str = Field(..., description="Fee")
    fee_ccy: str = Field(..., description="Fee currency")
    ts: str = Field(..., description="Trade timestamp")

class ModifyOKXOrderRequest(BaseModel):
    inst_id: str = Field(..., description="Instrument ID")
    ord_id: Optional[str] = Field(None, description="Order ID")
    cl_ord_id: Optional[str] = Field(None, description="Client order ID")
    req_id: Optional[str] = Field(None, description="Request ID")
    new_sz: Optional[str] = Field(None, description="New quantity")
    new_px: Optional[str] = Field(None, description="New price")

class CancelOKXOrderRequest(BaseModel):
    inst_id: str = Field(..., description="Instrument ID")
    ord_id: Optional[str] = Field(None, description="Order ID")
    cl_ord_id: Optional[str] = Field(None, description="Client order ID")

class CloseOKXPositionRequest(BaseModel):
    inst_id: str = Field(..., description="Instrument ID")
    mgn_mode: str = Field(..., description="Margin mode: cross, isolated")
    pos_side: Optional[str] = Field(None, description="Position side: net (for spot/margin), long/short (for derivatives)")
    ccy: Optional[str] = Field(None, description="Currency for margin trading")
    auto_cxl: Optional[bool] = Field(None, description="Auto cancel when market close")
    cl_ord_id: Optional[str] = Field(None, description="Client order ID")
    tag: Optional[str] = Field(None, description="Order tag")

class CloseOKXPositionResponse(BaseModel):
    inst_id: str = Field(..., description="Instrument ID")
    pos_side: Optional[str] = Field(None, description="Position side")
    cl_ord_id: Optional[str] = Field(None, description="Client order ID")
    tag: Optional[str] = Field(None, description="Order tag")