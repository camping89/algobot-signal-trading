from pydantic import BaseModel, Field
from typing import Optional, List
from decimal import Decimal
from datetime import datetime

class OKXAccount(BaseModel):
    u_time: str = Field(..., alias="uTime", description="Update time")
    total_eq: str = Field(..., alias="totalEq", description="Total equity in USD")
    adj_eq: Optional[str] = Field(None, alias="adjEq", description="Adjusted equity in USD")
    iso_eq: str = Field(..., alias="isoEq", description="Isolated margin equity in USD")
    ord_froz: str = Field(..., alias="ordFroz", description="Cross margin frozen for pending orders in USD")
    imr: str = Field(..., description="Initial margin requirement in USD")
    mmr: str = Field(..., description="Maintenance margin requirement in USD")
    notional_usd: str = Field(..., alias="notionalUsd", description="Notional value in USD")
    mgn_ratio: str = Field(..., alias="mgnRatio", description="Margin ratio")
    
    model_config = {"populate_by_name": True}

class OKXAccountConfig(BaseModel):
    acct_lv: str = Field(..., alias="acctLv", description="Account level")
    pos_mode: str = Field(..., alias="posMode", description="Position mode")
    auto_loan: bool = Field(..., alias="autoLoan", description="Auto loan")
    greeks_type: str = Field(..., alias="greeksType", description="Greeks type")
    level: str = Field(..., description="Level")
    level_tmp: str = Field(..., alias="levelTmp", description="Temporary level")
    ct_iso_mode: str = Field(..., alias="ctIsoMode", description="Contract isolated mode")
    mgn_iso_mode: str = Field(..., alias="mgnIsoMode", description="Margin isolated mode")
    spot_offset_type: str = Field(..., alias="spotOffsetType", description="Spot offset type")
    role_type: str = Field(..., alias="roleType", description="Role type")
    trade_role: str = Field(..., alias="tradeRole", description="Trade role")
    op_auth: str = Field(..., alias="opAuth", description="Operation authority")
    kycLv: str = Field(..., description="KYC level")
    ip: str = Field(..., description="IP address")
    perm: str = Field(..., description="Permission")
    label: str = Field(..., description="Label")
    uid: str = Field(..., description="User ID")
    
    model_config = {"populate_by_name": True}

class OKXBalance(BaseModel):
    u_time: str = Field(..., description="Update time")
    ccy: str = Field(..., description="Currency")
    bal: str = Field(..., description="Balance")
    frozen_bal: str = Field(..., description="Frozen balance")
    avail_bal: str = Field(..., description="Available balance")
    cash_bal: str = Field(..., description="Cash balance")
    eq_usd: str = Field(..., description="USD equity")
    upl: str = Field(..., description="Unrealized P&L")
    ord_frozen: str = Field(..., description="Frozen for orders")
    stgy_eq: str = Field(..., description="Strategy equity")
    spot_in_use_amt: Optional[str] = Field(None, description="Spot in use amount")
    iso_eq: str = Field(..., description="Isolated margin equity")
    max_loan: str = Field(..., description="Max loan")
    mgn_ratio: str = Field(..., description="Margin ratio")
    interest: str = Field(..., description="Interest")
    twap: str = Field(..., description="TWAP price")
    max_withdraw: str = Field(..., description="Max withdrawable")
    not_usd: str = Field(..., description="Notional USD")
    coin_usd_price: str = Field(..., description="USD price")
    borrowed: str = Field(..., description="Borrowed amount")

class OKXLeverage(BaseModel):
    inst_id: str = Field(..., description="Instrument ID")
    mgn_mode: str = Field(..., description="Margin mode")
    pos_side: str = Field(..., description="Position side")
    lever: str = Field(..., description="Leverage")

class OKXMaxSize(BaseModel):
    inst_id: str = Field(..., description="Instrument ID")
    ccy: str = Field(..., description="Currency")
    max_buy: str = Field(..., description="Max buy")
    max_sell: str = Field(..., description="Max sell")

class OKXMaxAvailSize(BaseModel):
    inst_id: str = Field(..., description="Instrument ID")
    avail_buy: str = Field(..., description="Available buy")
    avail_sell: str = Field(..., description="Available sell")

class OKXMarginBalance(BaseModel):
    inst_id: str = Field(..., description="Instrument ID")
    pos_id: str = Field(..., description="Position ID")
    mgn_bal: str = Field(..., description="Margin balance")
    mgn_ratio: str = Field(..., description="Margin ratio")
    max_add: str = Field(..., description="Max add")
    max_reduce: str = Field(..., description="Max reduce")

class OKXGreeks(BaseModel):
    ccy: str = Field(..., description="Currency")
    delta_bs: str = Field(..., description="Delta (BS)")
    gamma_bs: str = Field(..., description="Gamma (BS)") 
    theta_bs: str = Field(..., description="Theta (BS)")
    vega_bs: str = Field(..., description="Vega (BS)")
    delta_pa: str = Field(..., description="Delta (PA)")
    gamma_pa: str = Field(..., description="Gamma (PA)")
    theta_pa: str = Field(..., description="Theta (PA)")
    vega_pa: str = Field(..., description="Vega (PA)")
    ts: str = Field(..., description="Timestamp")

class OKXIsolatedMarginMode(BaseModel):
    iso_mode: str = Field(..., description="Isolated mode")

class OKXMarginMode(BaseModel):
    acct_lv: str = Field(..., description="Account level")

class OKXPositionMode(BaseModel):
    pos_mode: str = Field(..., description="Position mode")

class OKXFeeRate(BaseModel):
    level: str = Field(..., description="Level")
    taker: str = Field(..., description="Taker fee rate")
    maker: str = Field(..., description="Maker fee rate")
    delivery: str = Field(..., description="Delivery fee rate")
    exercise: str = Field(..., description="Exercise fee rate")
    inst_type: str = Field(..., description="Instrument type")
    ts: str = Field(..., description="Timestamp")