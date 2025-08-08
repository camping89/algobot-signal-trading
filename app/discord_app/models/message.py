from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ReplyToMessage(BaseModel):
    message_id: str
    author: str
    content: str
    attachments: List[str] = []


class DiscordMessage(BaseModel):
    message_id: str
    content: str
    attachments: List[str] = []
    reply_to: Optional[ReplyToMessage] = None


class MessageGroup(BaseModel):
    group_id: int
    timestamp: str
    username: str
    messages: List[DiscordMessage] = []


class DiscordData(BaseModel):
    username: str
    total_messages: int
    exported_count: int
    timespan: dict
    message_groups: List[MessageGroup] = []
    created_at: datetime = datetime.now()
    discord_channel_id: str
    target_user_id: str


class DiscordFetchRequest(BaseModel):
    discord_token: Optional[str] = None
    channel_id: Optional[str] = None
    target_user_id: Optional[str] = None
    limit: int = 100