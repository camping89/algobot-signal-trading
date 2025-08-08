from pydantic_settings import BaseSettings
from typing import Optional

class DiscordConfig(BaseSettings):
    # Discord Message Fetching Settings
    DISCORD_USER_TOKEN: Optional[str] = None
    DISCORD_CHANNEL_ID: Optional[str] = None
    TARGET_USER_ID: Optional[str] = None
    
    # MongoDB settings
    MONGODB_URL: str
    MONGODB_DB: str

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

discord_settings = DiscordConfig()