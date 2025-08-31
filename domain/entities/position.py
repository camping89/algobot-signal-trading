"""Trading position aggregate root"""
from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from datetime import datetime
from domain.common.enums import OrderType

class Position(BaseModel):
    """Trading position aggregate root"""
    ticket: int = Field(..., description="Position ticket/order ID")
    symbol: str = Field(..., description="Trading symbol")
    order_type: OrderType = Field(..., description="Order type (BUY/SELL)")
    volume: Decimal = Field(..., description="Trading volume")
    open_price: Decimal = Field(..., description="Position open price")
    stop_loss: Optional[Decimal] = Field(None, description="Stop loss level")
    take_profit: Optional[Decimal] = Field(None, description="Take profit level")
    profit: Decimal = Field(..., description="Current profit")
    open_time: datetime = Field(..., description="Position open time")