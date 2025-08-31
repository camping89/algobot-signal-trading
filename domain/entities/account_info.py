"""Trading account aggregate root"""
from pydantic import BaseModel, Field
from decimal import Decimal

class AccountInfo(BaseModel):
    """Trading account aggregate root"""
    balance: Decimal = Field(..., description="Account balance")
    equity: Decimal = Field(..., description="Account equity")
    margin: Decimal = Field(..., description="Used margin")
    free_margin: Decimal = Field(..., description="Free margin")
    positions_count: int = Field(..., description="Number of open positions")
    profit: Decimal = Field(..., description="Current profit")
    leverage: int = Field(..., description="Account leverage")
    currency: str = Field(..., description="Account currency")
    trade_allowed: bool = Field(..., description="Trading allowed flag")