from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import uvicorn
import time
import os
from contextlib import asynccontextmanager
from app.trading.config import trading_settings

from app.trading.routers.okx import trading as okx_trading, market as okx_market, account as okx_account
from app.trading.routers.okx import algo_trading

# Service dependency injection
from shared.service_registry import init_services, get_services, shutdown_services

# Global middleware and exception handlers
from shared.middleware import setup_exception_handlers, CorrelationMiddleware

# Health checks
from shared.health import create_health_router

# Initialize dependency injection container
services = init_services()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Trading service lifespan with dependency injection"""
    logger.info("--------------------------------------------")
    logger.info("| STARTUP - TRADING APP                    |")
    logger.info("--------------------------------------------")
    # Startup
    try:
        # Initialize all services using dependency injection
        initialization_results = await services.container.initialize_all_services()
        logger.info(f"Service initialization results: {initialization_results}")
        
        
        # Connect to OKX if enabled  
        if trading_settings.OKX_ENABLED:
            okx_base = services.okx_base_service
            okx_connected = await okx_base.connect(
                api_key=trading_settings.OKX_API_KEY,
                secret_key=trading_settings.OKX_SECRET_KEY,
                passphrase=trading_settings.OKX_PASSPHRASE,
                is_sandbox=trading_settings.OKX_IS_SANDBOX
            )
            if okx_connected:
                logger.info("OKX connection established")
        
            
    except Exception as e:
        logger.error(f"Trading service startup error: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    try:
        
        if services.okx_base_service.initialized:
            logger.info("Shutting down OKX connection")
            await services.okx_base_service.shutdown()
        
        # Shutdown all services
        await shutdown_services()
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

app = FastAPI(
    title="Trading API",
    description="OKX trading service with enhanced error handling and correlation tracking",
    version="1.0.0",
    lifespan=lifespan
)

# Add correlation ID middleware (should be first)
app.add_middleware(
    CorrelationMiddleware,
    enable_logging=True,
    enable_timing=True
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Correlation-ID", "X-Process-Time"]
)

# Setup global exception handlers
setup_exception_handlers(app)

# Create and include comprehensive health router
health_services = {
    "okx_base_service": services.okx_base_service,
    # Add more services as needed
}
health_router = create_health_router(
    require_auth_for_details=False,  # Set to True in production for security
    services=health_services
)
app.include_router(health_router)


# Include OKX routers with dependency injection
app.include_router(okx_trading.get_router(services.okx_trading_service), prefix="/okx")
app.include_router(okx_market.get_router(services.okx_market_service), prefix="/okx")
app.include_router(okx_account.get_router(services.okx_account_service), prefix="/okx")
app.include_router(algo_trading.get_router(services.okx_algo_service), prefix="/okx")

if __name__ == "__main__":
    uvicorn.run("app.trading.main:app", host="0.0.0.0", port=3010, reload=True)