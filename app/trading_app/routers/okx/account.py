from fastapi import APIRouter, HTTPException, Query
from app.trading_app.services.okx.okx_account_service import OKXAccountService
from typing import Optional

def get_router(account_service: OKXAccountService) -> APIRouter:
    router = APIRouter(prefix="/account", tags=["OKX Account"])

    @router.get("/info",
        summary="Get Account Information",
        description="Get account overview information")
    async def get_account_info():
        """
        Get comprehensive account balance and equity information
        
        This endpoint provides a complete overview of your account's financial status:
        
        **Response includes:**
        - **Total Equity**: Total account value in USD
        - **Adjusted Equity**: Risk-adjusted equity value
        - **Isolated Margin Equity**: Equity in isolated margin positions
        - **Order Frozen**: Funds locked in pending orders
        - **Initial Margin Requirement**: Required margin for current positions
        - **Maintenance Margin**: Minimum margin to avoid liquidation
        - **Margin Ratio**: Current margin health ratio
        - **Notional USD**: Total notional value of positions
        
        **Use cases:**
        - Account health monitoring
        - Risk management calculations
        - Portfolio value tracking
        - Margin utilization analysis
        """
        try:
            account_info = await account_service.get_account_info()
            
            if not account_info:
                raise HTTPException(status_code=404, detail="Account information not found")
                
            return {
                "status": "success",
                "data": account_info
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/balances",
        summary="Get Account Balances",
        description="Get account balances for all or specific currency")
    async def get_balances(ccy: Optional[str] = Query(default=None, description="Currency filter")):
        """
        Get detailed balance information for all currencies or a specific one
        
        This endpoint provides granular balance data for portfolio management:
        
        **Query Parameters:**
        - **ccy**: Currency filter (e.g., "BTC", "USDT", "ETH") - optional
        
        **Response includes (per currency):**
        - **Total Balance**: Complete holdings
        - **Available Balance**: Funds available for trading
        - **Frozen Balance**: Funds locked in orders/positions
        - **Cash Balance**: Spot trading balance
        - **USD Equity**: USD equivalent value
        - **Unrealized P&L**: Open position profit/loss
        - **Interest**: Accrued interest (margin accounts)
        - **Max Withdrawable**: Maximum amount that can be withdrawn
        
        **Examples:**
        - All balances: `/balances`
        - Bitcoin only: `/balances?ccy=BTC`
        - USDT only: `/balances?ccy=USDT`
        """
        try:
            balances = await account_service.get_balances(ccy)
            
            return {
                "status": "success",
                "data": balances,
                "count": len(balances)
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/positions",
        summary="Get Positions",
        description="Get account positions")
    async def get_positions(
        inst_type: Optional[str] = Query(default=None, description="Instrument type filter"),
        inst_id: Optional[str] = Query(default=None, description="Instrument ID filter")
    ):
        """
        Get all open positions with detailed performance metrics
        
        This endpoint provides comprehensive position information for active derivatives positions:
        
        **Query Parameters:**
        - **inst_type**: Filter by instrument type
          - **MARGIN**: Margin trading positions
          - **SWAP**: Perpetual swap positions
          - **FUTURES**: Futures contract positions
          - **OPTION**: Options positions
        - **inst_id**: Filter by specific instrument (e.g., "BTC-USDT-SWAP")
        
        **Response includes (per position):**
        - **Position Size**: Current position quantity
        - **Average Price**: Average entry price
        - **Mark Price**: Current mark price for liquidation
        - **Unrealized P&L**: Current profit/loss
        - **P&L Ratio**: Profit/loss percentage
        - **Margin**: Position margin requirement
        - **Margin Ratio**: Current margin health
        - **Leverage**: Applied leverage ratio
        - **Liquidation Price**: Price at which position gets liquidated
        - **ADL**: Auto-deleveraging indicator
        
        **Use cases:**
        - Portfolio performance monitoring
        - Risk management and position sizing
        - P&L tracking across instruments
        """
        try:
            positions = await account_service.get_positions(inst_type, inst_id)
            
            return {
                "status": "success",
                "data": positions,
                "count": len(positions)
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/leverage/{inst_id}",
        summary="Get Leverage",
        description="Get leverage information for an instrument")
    async def get_leverage(
        inst_id: str,
        mgn_mode: str = Query(..., description="Margin mode (isolated, cross)")
    ):
        """
        Get leverage information:
        - inst_id: Instrument ID
        - mgn_mode: Margin mode (isolated, cross)
        
        Returns:
        - Current leverage settings for the instrument
        """
        try:
            leverage = await account_service.get_leverage(inst_id, mgn_mode)
            
            if not leverage:
                raise HTTPException(status_code=404, detail=f"Leverage info not found for {inst_id}")
                
            return {
                "status": "success",
                "data": leverage
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/leverage/{inst_id}",
        summary="Set Leverage",
        description="Set leverage for an instrument")
    async def set_leverage(
        inst_id: str,
        lever: str = Query(..., description="Leverage value"),
        mgn_mode: str = Query(..., description="Margin mode (isolated, cross)"),
        pos_side: Optional[str] = Query(default=None, description="Position side (long, short, net)")
    ):
        """
        Set leverage for an instrument:
        - inst_id: Instrument ID
        - lever: Leverage value (e.g., "10")
        - mgn_mode: Margin mode (isolated, cross)
        - pos_side: Position side (long, short, net) - required for long/short mode
        
        Returns:
        - Success status of leverage change
        """
        try:
            success = await account_service.set_leverage(inst_id, lever, mgn_mode, pos_side)
            
            if not success:
                raise HTTPException(status_code=400, detail="Failed to set leverage")
                
            return {
                "status": "success",
                "message": f"Leverage set to {lever}x for {inst_id}"
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/max-size/{inst_id}",
        summary="Get Maximum Size",
        description="Get maximum tradable size for an instrument")
    async def get_max_size(
        inst_id: str,
        td_mode: str = Query(..., description="Trade mode (cash, cross, isolated)"),
        ccy: Optional[str] = Query(default=None, description="Currency"),
        px: Optional[str] = Query(default=None, description="Price")
    ):
        """
        Get maximum tradable size:
        - inst_id: Instrument ID
        - td_mode: Trade mode (cash, cross, isolated)
        - ccy: Currency (optional)
        - px: Price (optional)
        
        Returns:
        - Maximum buy and sell sizes available
        """
        try:
            max_size = await account_service.get_max_size(inst_id, td_mode, ccy, px)
            
            if not max_size:
                raise HTTPException(status_code=404, detail=f"Max size info not found for {inst_id}")
                
            return {
                "status": "success",
                "data": max_size
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/max-avail-size/{inst_id}",
        summary="Get Maximum Available Size",
        description="Get maximum available size for trading")
    async def get_max_avail_size(
        inst_id: str,
        td_mode: str = Query(..., description="Trade mode (cash, cross, isolated)"),
        ccy: Optional[str] = Query(default=None, description="Currency"),
        reduce_only: Optional[bool] = Query(default=None, description="Reduce only flag")
    ):
        """
        Get maximum available size:
        - inst_id: Instrument ID
        - td_mode: Trade mode (cash, cross, isolated)
        - ccy: Currency (optional)
        - reduce_only: Reduce only flag (optional)
        
        Returns:
        - Maximum available buy and sell sizes
        """
        try:
            max_avail = await account_service.get_max_avail_size(inst_id, td_mode, ccy, reduce_only)
            
            if not max_avail:
                raise HTTPException(status_code=404, detail=f"Max available size not found for {inst_id}")
                
            return {
                "status": "success",
                "data": max_avail
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/fee-rates",
        summary="Get Fee Rates",
        description="Get trading fee rates")
    async def get_fee_rates(
        inst_type: str = Query(..., description="Instrument type"),
        inst_id: Optional[str] = Query(default=None, description="Instrument ID"),
        uly: Optional[str] = Query(default=None, description="Underlying"),
        inst_family: Optional[str] = Query(default=None, description="Instrument family")
    ):
        """
        Get trading fee rates:
        - inst_type: Instrument type (SPOT, MARGIN, SWAP, FUTURES, OPTION)
        - inst_id: Instrument ID (optional)
        - uly: Underlying (optional)
        - inst_family: Instrument family (optional)
        
        Returns:
        - Trading fee rates for maker and taker orders
        """
        try:
            fee_rates = await account_service.get_fee_rates(inst_type, inst_id, uly, inst_family)
            
            return {
                "status": "success",
                "data": fee_rates,
                "count": len(fee_rates)
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/position-mode",
        summary="Get Position Mode",
        description="Get account position mode")
    async def get_position_mode():
        """
        Get account position mode:
        
        Returns:
        - Current position mode (long_short_mode or net_mode)
        """
        try:
            pos_mode = await account_service.get_position_mode()
            
            if not pos_mode:
                raise HTTPException(status_code=404, detail="Position mode not found")
                
            return {
                "status": "success",
                "data": {
                    "position_mode": pos_mode
                }
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/position-mode",
        summary="Set Position Mode", 
        description="Set account position mode")
    async def set_position_mode(
        pos_mode: str = Query(..., description="Position mode (long_short_mode or net_mode)")
    ):
        """
        Set account position mode:
        - pos_mode: Position mode (long_short_mode or net_mode)
        
        Returns:
        - Success status of position mode change
        """
        try:
            success = await account_service.set_position_mode(pos_mode)
            
            if not success:
                raise HTTPException(status_code=400, detail="Failed to set position mode")
                
            return {
                "status": "success",
                "message": f"Position mode set to {pos_mode}"
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return router