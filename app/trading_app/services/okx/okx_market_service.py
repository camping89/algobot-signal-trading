from typing import List, Optional, Dict, Any
import logging
from .okx_base_service import OKXBaseService
from app.trading_app.models.okx.market import (
    OKXKline, OKXOrderBook, OKXTrade, OKX24HrStats,
    OKXFundingRate, OKXMarkPrice, OKXIndexPrice, 
    OKXOpenInterest, OKXLimitPrice
)
from app.trading_app.models.okx.trade import OKXTicker, OKXInstrument

logger = logging.getLogger(__name__)

class OKXMarketService:
    """
    Service for handling market data operations in OKX.
    Provides functionality for getting market information, prices, and trading data.
    """
    
    def __init__(self, base_service: OKXBaseService):
        """
        Initialize market service with base OKX connection.
        
        Parameters:
        - base_service: Base OKX service for connection management
        """
        self.base_service = base_service

    @property
    def initialized(self):
        """Check if market service is initialized and connected"""
        return self.base_service.initialized

    async def get_ticker(self, inst_id: str) -> Optional[OKXTicker]:
        """
        Get ticker information for a specific instrument
        
        Args:
            inst_id: Instrument ID (e.g., BTC-USDT)
            
        Returns:
            Optional[OKXTicker]: Ticker data if successful
        """
        if not await self.base_service.ensure_connected():
            return None

        try:
            result = self.base_service.market_api.get_ticker(instId=inst_id)
            
            if not result or 'data' not in result or not result['data']:
                logger.error(f"No ticker data for {inst_id}")
                return None

            ticker_data = result['data'][0]
            return OKXTicker(
                inst_id=ticker_data['instId'],
                last=ticker_data['last'],
                last_sz=ticker_data['lastSz'],
                ask_px=ticker_data['askPx'],
                ask_sz=ticker_data['askSz'],
                bid_px=ticker_data['bidPx'],
                bid_sz=ticker_data['bidSz'],
                open_24h=ticker_data['open24h'],
                high_24h=ticker_data['high24h'],
                low_24h=ticker_data['low24h'],
                vol_24h=ticker_data['vol24h'],
                vol_ccy_24h=ticker_data['volCcy24h'],
                sod_utc0=ticker_data['sodUtc0'],
                sod_utc8=ticker_data['sodUtc8'],
                ts=ticker_data['ts']
            )

        except Exception as e:
            logger.error(f"Error getting ticker for {inst_id}: {str(e)}")
            return None

    async def get_all_tickers(self, inst_type: str = "SPOT") -> List[OKXTicker]:
        """
        Get ticker information for all instruments of a specific type
        
        Args:
            inst_type: Instrument type (SPOT, SWAP, FUTURES, OPTION)
            
        Returns:
            List[OKXTicker]: List of ticker data
        """
        if not await self.base_service.ensure_connected():
            return []

        try:
            result = self.base_service.market_api.get_tickers(instType=inst_type)
            
            if not result or 'data' not in result:
                return []

            tickers = []
            for ticker_data in result['data']:
                try:
                    ticker = OKXTicker(
                        inst_id=ticker_data['instId'],
                        last=ticker_data['last'],
                        last_sz=ticker_data['lastSz'],
                        ask_px=ticker_data['askPx'],
                        ask_sz=ticker_data['askSz'],
                        bid_px=ticker_data['bidPx'],
                        bid_sz=ticker_data['bidSz'],
                        open_24h=ticker_data['open24h'],
                        high_24h=ticker_data['high24h'],
                        low_24h=ticker_data['low24h'],
                        vol_24h=ticker_data['vol24h'],
                        vol_ccy_24h=ticker_data['volCcy24h'],
                        sod_utc0=ticker_data['sodUtc0'],
                        sod_utc8=ticker_data['sodUtc8'],
                        ts=ticker_data['ts']
                    )
                    tickers.append(ticker)
                except Exception as e:
                    logger.warning(f"Failed to parse ticker data: {e}")
                    continue
                    
            return tickers

        except Exception as e:
            logger.error(f"Error getting all tickers: {str(e)}")
            return []

    async def get_orderbook(self, inst_id: str, sz: str = "20") -> Optional[OKXOrderBook]:
        """
        Get order book for a specific instrument
        
        Args:
            inst_id: Instrument ID
            sz: Order book depth (1, 5, 10, 20, 50, 100, 200, 400)
            
        Returns:
            Optional[OKXOrderBook]: Order book data
        """
        if not await self.base_service.ensure_connected():
            return None

        try:
            result = self.base_service.market_api.get_orderbook(instId=inst_id, sz=sz)
            
            if not result or 'data' not in result or not result['data']:
                return None

            orderbook_data = result['data'][0]
            return OKXOrderBook(
                asks=orderbook_data['asks'],
                bids=orderbook_data['bids'],
                ts=orderbook_data['ts']
            )

        except Exception as e:
            logger.error(f"Error getting orderbook for {inst_id}: {str(e)}")
            return None

    async def get_trades(self, inst_id: str, limit: str = "100") -> List[OKXTrade]:
        """
        Get recent trades for a specific instrument
        
        Args:
            inst_id: Instrument ID
            limit: Number of trades to return
            
        Returns:
            List[OKXTrade]: List of recent trades
        """
        if not await self.base_service.ensure_connected():
            return []

        try:
            result = self.base_service.market_api.get_trades(instId=inst_id, limit=limit)
            
            if not result or 'data' not in result:
                return []

            trades = []
            for trade_data in result['data']:
                try:
                    trade = OKXTrade(
                        inst_id=trade_data['instId'],
                        trade_id=trade_data['tradeId'],
                        px=trade_data['px'],
                        sz=trade_data['sz'],
                        side=trade_data['side'],
                        ts=trade_data['ts']
                    )
                    trades.append(trade)
                except Exception as e:
                    logger.warning(f"Failed to parse trade data: {e}")
                    continue
                    
            return trades

        except Exception as e:
            logger.error(f"Error getting trades for {inst_id}: {str(e)}")
            return []

    async def get_klines(self, inst_id: str, bar: str = "1m", limit: str = "100", after: str = None, before: str = None) -> List[OKXKline]:
        """
        Get candlestick data for a specific instrument
        
        Args:
            inst_id: Instrument ID
            bar: Bar size (1m, 3m, 5m, 15m, 30m, 1H, 2H, 4H, 6H, 12H, 1D, 1W, 1M, 3M, 6M, 1Y)
            limit: Number of bars to return
            after: Request data after this timestamp
            before: Request data before this timestamp
            
        Returns:
            List[OKXKline]: List of candlestick data
        """
        if not await self.base_service.ensure_connected():
            return []

        try:
            params = {
                "instId": inst_id,
                "bar": bar,
                "limit": limit
            }
            
            if after:
                params["after"] = after
            if before:
                params["before"] = before

            result = self.base_service.market_api.get_candlesticks(**params)
            
            if not result or 'data' not in result:
                return []

            klines = []
            for kline_data in result['data']:
                try:
                    kline = OKXKline(
                        ts=kline_data[0],
                        o=kline_data[1],
                        h=kline_data[2],
                        l=kline_data[3],
                        c=kline_data[4],
                        vol=kline_data[5],
                        vol_ccy=kline_data[6],
                        vol_ccy_quote=kline_data[7],
                        confirm=kline_data[8]
                    )
                    klines.append(kline)
                except Exception as e:
                    logger.warning(f"Failed to parse kline data: {e}")
                    continue
                    
            return klines

        except Exception as e:
            logger.error(f"Error getting klines for {inst_id}: {str(e)}")
            return []

    async def get_24hr_stats(self, inst_id: str) -> Optional[OKX24HrStats]:
        """
        Get 24-hour statistics for a specific instrument
        
        Args:
            inst_id: Instrument ID
            
        Returns:
            Optional[OKX24HrStats]: 24-hour statistics
        """
        if not await self.base_service.ensure_connected():
            return None

        try:
            result = self.base_service.market_api.get_ticker(instId=inst_id)
            
            if not result or 'data' not in result or not result['data']:
                return None

            stats_data = result['data'][0]
            return OKX24HrStats(
                inst_id=stats_data['instId'],
                open_24h=stats_data['open24h'],
                high_24h=stats_data['high24h'],
                low_24h=stats_data['low24h'],
                sod_utc0=stats_data['sodUtc0'],
                sod_utc8=stats_data['sodUtc8'],
                vol_24h=stats_data['vol24h'],
                vol_ccy_24h=stats_data['volCcy24h'],
                ts=stats_data['ts']
            )

        except Exception as e:
            logger.error(f"Error getting 24hr stats for {inst_id}: {str(e)}")
            return None

    async def get_instruments(self, inst_type: str = "SPOT", uly: str = None) -> List[OKXInstrument]:
        """
        Get instruments information
        
        Args:
            inst_type: Instrument type (SPOT, MARGIN, SWAP, FUTURES, OPTION)
            uly: Underlying (for derivatives)
            
        Returns:
            List[OKXInstrument]: List of instruments
        """
        if not await self.base_service.ensure_connected():
            return []

        try:
            params = {
                "instType": inst_type
            }
            
            if uly:
                params["uly"] = uly

            result = self.base_service.public_api.get_instruments(**params)
            
            if not result or 'data' not in result:
                return []

            instruments = []
            for inst_data in result['data']:
                try:
                    instrument = OKXInstrument(**inst_data)
                    instruments.append(instrument)
                except Exception as e:
                    logger.warning(f"Failed to parse instrument data: {e}")
                    continue
                    
            return instruments

        except Exception as e:
            logger.error(f"Error getting instruments: {str(e)}")
            return []

    async def get_funding_rate(self, inst_id: str) -> Optional[OKXFundingRate]:
        """
        Get funding rate for perpetual swaps
        
        Args:
            inst_id: Instrument ID
            
        Returns:
            Optional[OKXFundingRate]: Funding rate data
        """
        if not await self.base_service.ensure_connected():
            return None

        try:
            result = self.base_service.public_api.get_funding_rate(instId=inst_id)
            
            if not result or 'data' not in result or not result['data']:
                return None

            funding_data = result['data'][0]
            return OKXFundingRate(
                inst_id=funding_data['instId'],
                funding_rate=funding_data['fundingRate'],
                next_funding_rate=funding_data['nextFundingRate'],
                funding_time=funding_data['fundingTime']
            )

        except Exception as e:
            logger.error(f"Error getting funding rate for {inst_id}: {str(e)}")
            return None

    async def get_mark_price(self, inst_id: str) -> Optional[OKXMarkPrice]:
        """
        Get mark price for futures and swaps
        
        Args:
            inst_id: Instrument ID
            
        Returns:
            Optional[OKXMarkPrice]: Mark price data
        """
        if not await self.base_service.ensure_connected():
            return None

        try:
            result = self.base_service.public_api.get_mark_price(instId=inst_id)
            
            if not result or 'data' not in result or not result['data']:
                return None

            mark_data = result['data'][0]
            return OKXMarkPrice(
                inst_id=mark_data['instId'],
                mark_px=mark_data['markPx'],
                ts=mark_data['ts']
            )

        except Exception as e:
            logger.error(f"Error getting mark price for {inst_id}: {str(e)}")
            return None