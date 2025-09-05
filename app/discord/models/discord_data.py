"""Discord data model"""
from pydantic import BaseModel
from typing import List
from datetime import datetime
from .discord_message_group import DiscordMessageGroup


class DiscordData(BaseModel):
    username: str
    total_messages: int
    exported_count: int
    timespan: dict
    message_groups: List[DiscordMessageGroup] = []
    created_at: datetime = datetime.now()
    discord_channel_id: str
    target_user_id: str
