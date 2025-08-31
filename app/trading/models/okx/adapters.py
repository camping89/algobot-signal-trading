"""OKX platform-specific models and adapters"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from decimal import Decimal
from datetime import datetime
from domain.entities.position import Position
from domain.entities.trade_request import TradeRequest
from domain.entities.trade_response import TradeResponse
from domain.entities.account_info import AccountInfo
from domain.common.enums import OrderType

# OKX-specific enums
class OKXOrderSide(str):
    BUY = "buy"
    SELL = "sell"

class OKXTradeMode(str):
    CASH = "cash"
    CROSS = "cross"
    ISOLATED = "isolated"

class OKXOrderType(str):
    LIMIT = "limit"
    MARKET = "market"
    POST_ONLY = "post_only"
    FOK = "fok"
    IOC = "ioc"

class OKXPositionSide(str):
    LONG = "long"
    SHORT = "short"
    NET = "net"

class OKXTradeRequest(BaseModel):
    """OKX-specific trade request"""
    inst_id: str = Field(..., description="Instrument ID")
    td_mode: OKXTradeMode = Field(..., description="Trade mode")
    side: OKXOrderSide = Field(..., description="Order side")
    ord_type: OKXOrderType = Field(..., description="Order type")
    sz: str = Field(..., description="Order size")
    px: Optional[str] = Field(None, description="Order price")
    ccy: Optional[str] = Field(None, description="Currency")
    cl_ord_id: Optional[str] = Field(None, description="Client order ID")
    tag: Optional[str] = Field(None, description="Order tag")

class OKXPosition(BaseModel):
    """OKX-specific position model"""
    inst_id: str = Field(..., description="Instrument ID")
    pos_id: str = Field(..., description="Position ID")
    trade_id: str = Field(..., description="Trade ID")
    pos_side: OKXPositionSide = Field(..., description="Position side")
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
    """OKX-specific account information"""
    total_eq: Decimal = Field(..., description="Total equity")
    adj_eq: Optional[Decimal] = Field(None, description="Adjusted equity")
    iso_eq: Decimal = Field(..., description="Isolated margin equity")
    ord_froz: Decimal = Field(..., description="Margin frozen for pending orders")
    imr: Decimal = Field(..., description="Initial margin requirement")
    mmr: Decimal = Field(..., description="Maintenance margin requirement")
    mfr: Decimal = Field(..., description="Margin frozen for open positions")
    u_time: str = Field(..., description="Update time")

class OKXAccountAdapter:
    """Adapter to convert between OKX and domain models"""
    
    @staticmethod
    def to_domain_account(okx_account_info: OKXAccountInfo) -> AccountInfo:
        """Convert OKX account info to domain AccountInfo"""
        return AccountInfo(
            balance=okx_account_info.total_eq,
            equity=okx_account_info.adj_eq or okx_account_info.total_eq,
            margin=okx_account_info.imr,
            free_margin=okx_account_info.total_eq - okx_account_info.imr,
            positions_count=0,  # Would need separate call to get this
            profit=Decimal('0'),  # Would need separate calculation
            leverage=1,  # OKX has per-instrument leverage
            currency="USDT",  # Default, could be configurable
            trade_allowed=True  # Would need separate check
        )
    
    @staticmethod
    def to_okx_request(domain_request: TradeRequest) -> OKXTradeRequest:
        """Convert domain TradeRequest to OKX-specific request"""
        okx_side = OKXOrderSide.BUY if domain_request.order_type == OrderType.BUY else OKXOrderSide.SELL
        
        return OKXTradeRequest(
            inst_id=domain_request.symbol,
            td_mode=OKXTradeMode.CASH,  # Default trade mode
            side=okx_side,
            ord_type=OKXOrderType.MARKET,  # Default to market order
            sz=str(domain_request.amount),
            tag=domain_request.comment
        )

class OKXTicker(BaseModel):
    """OKX ticker information"""
    inst_id: str
    last: str
    last_sz: str
    ask_px: str
    ask_sz: str
    bid_px: str
    bid_sz: str
    open_24h: str
    high_24h: str
    low_24h: str
    vol_ccy_24h: str
    vol_24h: str
    ts: str
    sod_utc0: str
    sod_utc8: str

class OKXInstrument(BaseModel):
    """OKX instrument information"""
    inst_id: str
    uly: str
    inst_family: str
    inst_type: str
    tick_sz: str
    lot_sz: str
    min_sz: str
    ct_type: str
    ct_mult: str
    ct_val: str
    ct_val_ccy: str
    opt_type: Optional[str] = None
    stk: Optional[str] = None
    list_time: str
    exp_time: Optional[str] = None
    lever: str
    state: str