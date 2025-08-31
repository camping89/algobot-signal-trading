from pydantic_settings import BaseSettings
from typing import Optional

class TradingConfig(BaseSettings):
    OKX_API_KEY: str
    OKX_SECRET_KEY: str
    OKX_PASSPHRASE: str
    OKX_IS_SANDBOX: bool
    
    MONGODB_URL: str
    MONGODB_DB: str
    
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_CHAT_ID: str
    DISCORD_WEBHOOK_URL: str

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

trading_settings = TradingConfig()