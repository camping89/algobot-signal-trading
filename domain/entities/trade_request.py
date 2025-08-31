"""Universal trade request value object"""
from pydantic import BaseModel, Field
from typing import Optional
from domain.common.enums import OrderType

class TradeRequest(BaseModel):
    """Universal trade request value object"""
    symbol: str = Field(..., description="Trading symbol")
    order_type: OrderType = Field(..., description="Order type")
    amount: float = Field(..., description="Investment amount", gt=0)
    stop_loss: Optional[float] = Field(None, description="Stop loss level")
    take_profit: Optional[float] = Field(None, description="Take profit level")
    comment: Optional[str] = Field(None, description="Order comment")