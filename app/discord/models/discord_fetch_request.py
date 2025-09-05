"""Discord fetch request model"""
from pydantic import BaseModel
from typing import Optional


class DiscordFetchRequest(BaseModel):
    discord_token: Optional[str] = None
    channel_id: Optional[str] = None
    target_user_id: Optional[str] = None
    limit: int = 100
