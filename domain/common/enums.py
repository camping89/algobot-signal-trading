"""Common domain enums used across the system"""
from enum import Enum

class OrderType(str, Enum):
    """Universal order type for all trading platforms"""
    BUY = "BUY"
    SELL = "SELL"

class TimeFrame(str, Enum):
    """Standard timeframes for market analysis"""
    S1 = "S"
    S5 = "5S"
    S15 = "15S"
    S30 = "30S"
    M1 = "1"
    M3 = "3"
    M5 = "5"
    M15 = "15"
    M30 = "30"
    M45 = "45"
    H1 = "60"
    H2 = "120"
    H3 = "180"
    H4 = "240"
    D1 = "D"
    D5 = "5D"
    W1 = "W"
    MN1 = "M"
    Q1 = "3M"
    Y1 = "12M"

class SignalType(str, Enum):
    """Trading signal direction"""
    UP = "UP"
    DOWN = "DOWN"