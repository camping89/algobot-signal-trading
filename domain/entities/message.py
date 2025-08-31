"""Core message entity"""
from pydantic import BaseModel, Field
from datetime import datetime

class Message(BaseModel):
    """Core message entity"""
    message_id: str = Field(..., description="Unique message identifier")
    content: str = Field(..., description="Message content")
    author: str = Field(..., description="Message author")
    timestamp: datetime = Field(..., description="Message timestamp")
    platform: str = Field(..., description="Message platform (discord, telegram, etc)")
    channel_id: str = Field(..., description="Channel identifier")