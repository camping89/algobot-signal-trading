"""Discord message group model"""
from pydantic import BaseModel
from typing import List
from .discord_message import DiscordMessage


class DiscordMessageGroup(BaseModel):
    group_id: int
    timestamp: str
    username: str
    messages: List[DiscordMessage] = []
