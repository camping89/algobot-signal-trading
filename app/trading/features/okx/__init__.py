from .trading.router import router as trading_router
from .market.router import router as market_router
from .account.router import router as account_router
from .algo.router import router as algo_router

routers = [trading_router, market_router, account_router, algo_router]