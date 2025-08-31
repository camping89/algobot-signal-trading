"""Trading signal aggregate root"""
from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from datetime import datetime
from domain.common.enums import SignalType, TimeFrame

class TradingSignal(BaseModel):
    """Trading signal aggregate root"""
    signal_id: Optional[str] = Field(None, description="Signal unique identifier")
    symbol: str = Field(..., description="Trading symbol")
    signal_type: SignalType = Field(..., description="Signal direction")
    timeframe: TimeFrame = Field(..., description="Signal timeframe")
    entry_price: Optional[Decimal] = Field(None, description="Entry price")
    stop_loss: Optional[Decimal] = Field(None, description="Stop loss")
    take_profit: Optional[Decimal] = Field(None, description="Take profit")
    confidence: float = Field(default=0.5, description="Signal confidence (0-1)")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Signal creation time")
    source: str = Field(default="system", description="Signal source")
    metadata: dict = Field(default_factory=dict, description="Additional signal data")