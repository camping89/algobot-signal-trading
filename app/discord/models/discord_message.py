"""Discord message model"""
from pydantic import BaseModel
from typing import Optional, List
from .reply_to_message import ReplyToMessage


class DiscordMessage(BaseModel):
    message_id: str
    content: str
    attachments: List[str] = []
    reply_to: Optional[ReplyToMessage] = None
    embeds: List[dict] = []
    reactions: List[dict] = []
