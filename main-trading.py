from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import uvicorn
from contextlib import asynccontextmanager
from app.trading_app.config import trading_settings
from app.trading_app.models.mt5.notification import NotificationConfig

from app.trading_app.routers.mt5 import market_info, orders, history, position, risk_management, trading as mt5_trading, account as mt5_account, notification, automation, reporting, signal
from app.trading_app.routers.okx import trading as okx_trading, market as okx_market, account as okx_account
from app.trading_app.routers.okx import algo_trading

from app.trading_app.services.mt5.mt5_base_service import MT5BaseService
from app.trading_app.services.mt5.mt5_trading_service import MT5TradingService
from app.trading_app.services.mt5.mt5_market_service import MT5MarketService
from app.trading_app.services.mt5.mt5_order_service import MT5OrderService
from app.trading_app.services.mt5.mt5_position_service import MT5PositionService
from app.trading_app.services.mt5.mt5_history_service import MT5HistoryService
from app.trading_app.services.mt5.mt5_account_service import MT5AccountService
from app.trading_app.services.mt5.mt5_risk_service import MT5RiskService
from app.trading_app.services.mt5.mt5_notification_service import MT5NotificationService
from app.trading_app.services.mt5.mt5_automation_service import MT5AutomationService
from app.trading_app.services.mt5.mt5_reporting_service import MT5ReportingService
from app.trading_app.services.mt5.mt5_signal_service import MT5SignalService

from app.trading_app.services.okx.okx_base_service import OKXBaseService
from app.trading_app.services.okx.okx_trading_service import OKXTradingService
from app.trading_app.services.okx.okx_market_service import OKXMarketService
from app.trading_app.services.okx.okx_account_service import OKXAccountService
from app.trading_app.services.okx.okx_algo_service import OKXAlgoService

# Initialize services
mt5_base_service = MT5BaseService()
mt5_trading_service = MT5TradingService(mt5_base_service)
mt5_market_service = MT5MarketService(mt5_base_service)
mt5_order_service = MT5OrderService(mt5_base_service)
mt5_position_service = MT5PositionService(mt5_base_service)
mt5_history_service = MT5HistoryService(mt5_base_service)
mt5_account_service = MT5AccountService(mt5_base_service)
mt5_risk_service = MT5RiskService(mt5_base_service)
mt5_notification_service = MT5NotificationService(mt5_base_service)
mt5_automation_service = MT5AutomationService(mt5_base_service)
mt5_reporting_service = MT5ReportingService(mt5_base_service)
mt5_signal_service = MT5SignalService(mt5_base_service)

okx_base_service = OKXBaseService()
okx_trading_service = OKXTradingService(okx_base_service)
okx_market_service = OKXMarketService(okx_base_service)
okx_account_service = OKXAccountService(okx_base_service)
okx_algo_service = OKXAlgoService(okx_base_service)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Trading service lifespan"""
    # Startup
    try:
        # Connect to MT5
        mt5_connected = await mt5_base_service.connect(
            login=trading_settings.MT5_LOGIN,
            password=trading_settings.MT5_PASSWORD,
            server=trading_settings.MT5_SERVER
        )
        if mt5_connected:
            logger.info("MT5 connection established")
        
        # Connect to OKX
        okx_connected = await okx_base_service.connect(
            api_key=trading_settings.OKX_API_KEY,
            secret_key=trading_settings.OKX_SECRET_KEY,
            passphrase=trading_settings.OKX_PASSPHRASE,
            is_sandbox=trading_settings.OKX_IS_SANDBOX
        )
        if okx_connected:
            logger.info("OKX connection established")
        
        # Initialize notification service (only if MT5 connected)
        if mt5_connected:
            notification_config = NotificationConfig(
                telegram_token=trading_settings.TELEGRAM_BOT_TOKEN,
                telegram_chat_id=trading_settings.TELEGRAM_CHAT_ID,
                discord_webhook=trading_settings.DISCORD_WEBHOOK_URL,
            )
            await mt5_notification_service.initialize(notification_config)
            await mt5_automation_service.start_automation()
        
    except Exception as e:
        logger.error(f"Trading service startup error: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    if mt5_base_service.initialized:
        logger.info("Shutting down MT5 connection")
        await mt5_automation_service.stop_automation()
        await mt5_base_service.shutdown()
        
    if okx_base_service.initialized:
        logger.info("Shutting down OKX connection")
        await okx_base_service.shutdown()

app = FastAPI(
    title="Trading API",
    description="MT5 and OKX trading service",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    mt5_status = "connected" if mt5_base_service.initialized else "disconnected"
    okx_status = "connected" if okx_base_service.initialized else "disconnected"
    
    overall_status = "healthy" if (mt5_base_service.initialized or okx_base_service.initialized) else "unhealthy"
    
    return {
        "status": overall_status,
        "service": "trading",
        "services": {
            "mt5": mt5_status,
            "okx": okx_status
        }
    }

# Include MT5 routers
app.include_router(mt5_trading.get_router(mt5_trading_service, mt5_notification_service), prefix="/mt5")
app.include_router(market_info.get_router(mt5_market_service), prefix="/mt5")
app.include_router(orders.get_router(mt5_order_service), prefix="/mt5")
app.include_router(history.get_router(mt5_history_service), prefix="/mt5")
app.include_router(position.get_router(mt5_position_service, mt5_notification_service), prefix="/mt5")
app.include_router(mt5_account.get_router(mt5_account_service), prefix="/mt5")
app.include_router(risk_management.get_router(mt5_risk_service), prefix="/mt5")
app.include_router(notification.get_router(mt5_notification_service), prefix="/mt5")
app.include_router(automation.get_router(mt5_automation_service), prefix="/mt5")
app.include_router(reporting.get_router(mt5_reporting_service), prefix="/mt5")
app.include_router(signal.get_router(mt5_signal_service, mt5_notification_service), prefix="/mt5")

# Include OKX routers
app.include_router(okx_trading.get_router(okx_trading_service), prefix="/okx")
app.include_router(okx_market.get_router(okx_market_service), prefix="/okx")
app.include_router(okx_account.get_router(okx_account_service), prefix="/okx")
app.include_router(algo_trading.get_router(okx_algo_service), prefix="/okx")

if __name__ == "__main__":
    uvicorn.run("main-trading:app", host="0.0.0.0", port=3002, reload=True)