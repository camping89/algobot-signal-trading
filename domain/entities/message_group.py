"""Message group aggregate root"""
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
from domain.entities.message import Message

class MessageGroup(BaseModel):
    """Message group aggregate root"""
    group_id: str = Field(..., description="Group identifier")
    author: str = Field(..., description="Group author")
    timestamp: datetime = Field(..., description="Group timestamp")
    platform: str = Field(..., description="Platform identifier")
    channel_id: str = Field(..., description="Channel identifier")
    messages: List[Message] = Field(default_factory=list, description="Messages in group")