from fastapi import APIRouter, HTTPException, Query
from app.trading_app.services.okx.okx_market_service import OKXMarketService
from typing import List, Optional

def get_router(market_service: OKXMarketService) -> APIRouter:
    router = APIRouter(prefix="/market", tags=["OKX Market Data"])

    @router.get("/ticker/{inst_id}",
        summary="Get Ticker",
        description="Get ticker information for a specific instrument")
    async def get_ticker(inst_id: str):
        """
        Get real-time ticker information for a trading pair
        
        This endpoint provides comprehensive market data for a specific instrument:
        
        **Path Parameters:**
        - **inst_id**: Instrument identifier (e.g., "BTC-USDT", "ETH-BTC")
        
        **Response includes:**
        - **Last price**: Most recent trade price
        - **24h change**: Price change in last 24 hours (absolute and percentage)
        - **Volume**: Trading volume in last 24 hours
        - **High/Low**: 24-hour price range
        - **Best bid/ask**: Current best buy/sell prices
        - **Open interest**: For derivatives only
        
        **Examples:**
        - Bitcoin: `/ticker/BTC-USDT`
        - Ethereum: `/ticker/ETH-USDT`
        - Altcoin: `/ticker/ADA-USDT`
        """
        try:
            ticker = await market_service.get_ticker(inst_id)
            
            if not ticker:
                raise HTTPException(status_code=404, detail=f"Ticker data not found for {inst_id}")
                
            return {
                "status": "success",
                "data": ticker
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/tickers",
        summary="Get All Tickers",
        description="Get ticker information for all instruments of a specific type")
    async def get_all_tickers(inst_type: str = Query(default="SPOT", description="Instrument type")):
        """
        Get ticker information for all instruments of a specific type
        
        This endpoint retrieves market data for all trading pairs in a category:
        
        **Query Parameters:**
        - **inst_type**: Type of instruments to retrieve
          - **SPOT**: Spot trading pairs (BTC-USDT, ETH-USDT, etc.)
          - **SWAP**: Perpetual swaps (BTC-USDT-SWAP, ETH-USDT-SWAP)
          - **FUTURES**: Futures contracts (BTC-USDT-240329)
          - **OPTION**: Options contracts
          - **MARGIN**: Margin trading pairs
        
        **Use cases:**
        - Market overview and screening
        - Price monitoring across all pairs
        - Volume analysis and ranking
        - Building trading dashboards
        
        **Examples:**
        - All spot pairs: `?inst_type=SPOT`
        - All perpetual swaps: `?inst_type=SWAP`
        """
        try:
            tickers = await market_service.get_all_tickers(inst_type)
            
            return {
                "status": "success",
                "data": tickers,
                "count": len(tickers)
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/orderbook/{inst_id}",
        summary="Get Order Book",
        description="Get order book for a specific instrument")
    async def get_orderbook(
        inst_id: str,
        sz: str = Query(default="20", description="Order book depth")
    ):
        """
        Get order book for a specific instrument:
        - inst_id: Instrument ID
        - sz: Order book depth (1, 5, 10, 20, 50, 100, 200, 400)
        
        Returns:
        - Order book with bids and asks
        """
        try:
            orderbook = await market_service.get_orderbook(inst_id, sz)
            
            if not orderbook:
                raise HTTPException(status_code=404, detail=f"Order book not found for {inst_id}")
                
            return {
                "status": "success",
                "data": orderbook
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/trades/{inst_id}",
        summary="Get Recent Trades",
        description="Get recent trades for a specific instrument")
    async def get_trades(
        inst_id: str,
        limit: str = Query(default="100", description="Number of trades to return")
    ):
        """
        Get recent trades for a specific instrument:
        - inst_id: Instrument ID
        - limit: Number of trades to return (max 500)
        
        Returns:
        - List of recent trades with price, size, and timestamp
        """
        try:
            trades = await market_service.get_trades(inst_id, limit)
            
            return {
                "status": "success",
                "data": trades,
                "count": len(trades)
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/klines/{inst_id}",
        summary="Get Candlestick Data",
        description="Get candlestick/kline data for a specific instrument")
    async def get_klines(
        inst_id: str,
        bar: str = Query(default="1m", description="Bar size"),
        limit: str = Query(default="100", description="Number of bars"),
        after: Optional[str] = Query(default=None, description="Request data after this timestamp"),
        before: Optional[str] = Query(default=None, description="Request data before this timestamp")
    ):
        """
        Get historical candlestick (OHLCV) data for technical analysis
        
        This endpoint provides candlestick data essential for chart analysis and trading strategies:
        
        **Path Parameters:**
        - **inst_id**: Instrument identifier (e.g., "BTC-USDT")
        
        **Query Parameters:**
        - **bar**: Timeframe for each candlestick
          - **Minutes**: 1m, 3m, 5m, 15m, 30m
          - **Hours**: 1H, 2H, 4H, 6H, 12H
          - **Days**: 1D, 2D, 3D, 5D
          - **Weeks**: 1W, 2W
          - **Months**: 1M, 3M, 6M
          - **Years**: 1Y, 2Y
        - **limit**: Number of candlesticks (max 300, default 100)
        - **after/before**: Filter by timestamp for historical data
        
        **Response format**: [timestamp, open, high, low, close, volume, volume_in_quote_currency, volume_in_base_currency, confirm]
        
        **Use cases:**
        - Technical analysis and charting
        - Backtesting trading strategies
        - Market trend analysis
        """
        try:
            klines = await market_service.get_klines(
                inst_id=inst_id,
                bar=bar,
                limit=limit,
                after=after,
                before=before
            )
            
            return {
                "status": "success",
                "data": klines,
                "count": len(klines)
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/24hr-stats/{inst_id}",
        summary="Get 24h Statistics",
        description="Get 24-hour statistics for a specific instrument")
    async def get_24hr_stats(inst_id: str):
        """
        Get 24-hour statistics for a specific instrument:
        - inst_id: Instrument ID
        
        Returns:
        - 24-hour price and volume statistics
        """
        try:
            stats = await market_service.get_24hr_stats(inst_id)
            
            if not stats:
                raise HTTPException(status_code=404, detail=f"24hr stats not found for {inst_id}")
                
            return {
                "status": "success",
                "data": stats
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/instruments",
        summary="Get Instruments",
        description="Get instruments information")
    async def get_instruments(
        inst_type: str = Query(default="SPOT", description="Instrument type"),
        uly: Optional[str] = Query(default=None, description="Underlying")
    ):
        """
        Get instruments information:
        - inst_type: Instrument type (SPOT, MARGIN, SWAP, FUTURES, OPTION)
        - uly: Underlying (for derivatives)
        
        Returns:
        - List of available instruments with their specifications
        """
        try:
            instruments = await market_service.get_instruments(inst_type, uly)
            
            return {
                "status": "success",
                "data": instruments,
                "count": len(instruments)
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/funding-rate/{inst_id}",
        summary="Get Funding Rate",
        description="Get funding rate for perpetual swaps")
    async def get_funding_rate(inst_id: str):
        """
        Get funding rate for perpetual swaps:
        - inst_id: Instrument ID (must be a perpetual swap)
        
        Returns:
        - Current and next funding rate with funding time
        """
        try:
            funding_rate = await market_service.get_funding_rate(inst_id)
            
            if not funding_rate:
                raise HTTPException(status_code=404, detail=f"Funding rate not found for {inst_id}")
                
            return {
                "status": "success",
                "data": funding_rate
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/mark-price/{inst_id}",
        summary="Get Mark Price",
        description="Get mark price for futures and swaps")
    async def get_mark_price(inst_id: str):
        """
        Get mark price for futures and swaps:
        - inst_id: Instrument ID (futures or swap)
        
        Returns:
        - Mark price used for liquidation calculations
        """
        try:
            mark_price = await market_service.get_mark_price(inst_id)
            
            if not mark_price:
                raise HTTPException(status_code=404, detail=f"Mark price not found for {inst_id}")
                
            return {
                "status": "success",
                "data": mark_price
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return router