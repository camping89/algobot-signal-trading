from pydantic_settings import BaseSettings
from typing import Optional

class TradingConfig(BaseSettings):
    # MT5 Settings
    MT5_LOGIN: int
    MT5_PASSWORD: str
    MT5_SERVER: str
    
    # OKX Settings
    OKX_API_KEY: str
    OKX_SECRET_KEY: str
    OKX_PASSPHRASE: str
    OKX_IS_SANDBOX: bool
    
    # MongoDB Settings
    MONGODB_URL: str
    MONGODB_DB: str
    
    # Notification Settings
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_CHAT_ID: str
    DISCORD_WEBHOOK_URL: str

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

trading_settings = TradingConfig()