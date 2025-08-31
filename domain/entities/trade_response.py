"""Universal trade response value object"""
from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal

class TradeResponse(BaseModel):
    """Universal trade response value object"""
    order_id: int = Field(..., description="Order ID from broker")
    status: str = Field(..., description="Trade status")
    message: str = Field(..., description="Response message")
    executed_price: Optional[Decimal] = Field(None, description="Executed price")
    executed_volume: Optional[Decimal] = Field(None, description="Executed volume")