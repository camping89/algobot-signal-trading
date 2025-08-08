from fastapi import APIRouter, Depends
from typing import Optional
from app.trading_app.services.mt5.mt5_account_service import MT5AccountService
from app.trading_app.models.mt5.trade import AccountInfo

def get_router(service: MT5AccountService) -> APIRouter:
    router = APIRouter(prefix="/account", tags=["MT5 Account Information"])

    @router.get("/info", 
        response_model=Optional[AccountInfo],
        summary="Get Account Information",
        description="Retrieve detailed trading account information and balance")
    async def get_account_info():
        """
        Get account information including:
        - Balance
        - Equity
        - Margin
        - Free margin
        - Number of open positions
        """
        return await service.get_account_info()

    return router 