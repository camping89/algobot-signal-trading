from fastapi import APIRouter, HTTPException, Query, Depends
from app.trading.services.okx.okx_market_service import OKXMarketService
from typing import List, Optional
from shared.service_registry import get_services

router = APIRouter(prefix="/okx/market", tags=["OKX Market Data"])

def get_market_service() -> OKXMarketService:
    services = get_services()
    return services.okx_market_service

@router.get("/ticker/{inst_id}",
    summary="Get Ticker",
    description="Get ticker information for a specific instrument")
async def get_ticker(
    inst_id: str,
    market_service: OKXMarketService = Depends(get_market_service)
):
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
async def get_all_tickers(
    inst_type: str = Query(default="SPOT", description="Instrument type"),
    market_service: OKXMarketService = Depends(get_market_service)
):
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
    sz: str = Query(default="20", description="Order book depth"),
    market_service: OKXMarketService = Depends(get_market_service)
):
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
    limit: str = Query(default="100", description="Number of trades to return"),
    market_service: OKXMarketService = Depends(get_market_service)
):
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
    before: Optional[str] = Query(default=None, description="Request data before this timestamp"),
    market_service: OKXMarketService = Depends(get_market_service)
):
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
async def get_24hr_stats(
    inst_id: str,
    market_service: OKXMarketService = Depends(get_market_service)
):
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
    uly: Optional[str] = Query(default=None, description="Underlying"),
    market_service: OKXMarketService = Depends(get_market_service)
):
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
async def get_funding_rate(
    inst_id: str,
    market_service: OKXMarketService = Depends(get_market_service)
):
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
async def get_mark_price(
    inst_id: str,
    market_service: OKXMarketService = Depends(get_market_service)
):
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