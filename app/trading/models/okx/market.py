from pydantic import BaseModel, Field
from typing import Optional, List
from decimal import Decimal
from datetime import datetime

class OKXKline(BaseModel):
    ts: str = Field(..., description="Timestamp")
    o: str = Field(..., description="Open price")
    h: str = Field(..., description="High price")
    l: str = Field(..., description="Low price")
    c: str = Field(..., description="Close price")
    vol: str = Field(..., description="Trading volume")
    vol_ccy: str = Field(..., description="Trading volume in quote currency")
    vol_ccy_quote: str = Field(..., description="Trading volume in quote currency")
    confirm: str = Field(..., description="Confirmation status")

class OKXOrderBook(BaseModel):
    asks: List[List[str]] = Field(..., description="Ask orders [price, size, liquidated_orders, num_orders]")
    bids: List[List[str]] = Field(..., description="Bid orders [price, size, liquidated_orders, num_orders]")
    ts: str = Field(..., description="Timestamp")

class OKXTrade(BaseModel):
    inst_id: str = Field(..., description="Instrument ID")
    trade_id: str = Field(..., description="Trade ID")
    px: str = Field(..., description="Trade price")
    sz: str = Field(..., description="Trade size")
    side: str = Field(..., description="Trade side")
    ts: str = Field(..., description="Trade timestamp")

class OKX24HrStats(BaseModel):
    inst_id: str = Field(..., description="Instrument ID")
    open_24h: str = Field(..., description="24h opening price")
    high_24h: str = Field(..., description="24h highest price")  
    low_24h: str = Field(..., description="24h lowest price")
    sod_utc0: str = Field(..., description="Start of day price (UTC+0)")
    sod_utc8: str = Field(..., description="Start of day price (UTC+8)")
    vol_24h: str = Field(..., description="24h trading volume")
    vol_ccy_24h: str = Field(..., description="24h trading volume in quote currency")
    ts: str = Field(..., description="Timestamp")

class OKXFundingRate(BaseModel):
    inst_id: str = Field(..., description="Instrument ID")
    funding_rate: str = Field(..., description="Current funding rate")
    next_funding_rate: str = Field(..., description="Next funding rate")
    funding_time: str = Field(..., description="Funding time")

class OKXMarkPrice(BaseModel):
    inst_id: str = Field(..., description="Instrument ID") 
    mark_px: str = Field(..., description="Mark price")
    ts: str = Field(..., description="Timestamp")

class OKXIndexPrice(BaseModel):
    inst_id: str = Field(..., description="Instrument ID")
    idx_px: str = Field(..., description="Index price")
    ts: str = Field(..., description="Timestamp")

class OKXOpenInterest(BaseModel):
    inst_id: str = Field(..., description="Instrument ID")
    oi: str = Field(..., description="Open interest")
    oi_ccy: str = Field(..., description="Open interest in contracts")
    ts: str = Field(..., description="Timestamp")

class OKXLimitPrice(BaseModel):
    inst_id: str = Field(..., description="Instrument ID")
    buy_lmt: str = Field(..., description="Buy limit")
    sell_lmt: str = Field(..., description="Sell limit")
    ts: str = Field(..., description="Timestamp")