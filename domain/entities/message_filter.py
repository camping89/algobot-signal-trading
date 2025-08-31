"""Message filtering criteria value object"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class MessageFilter(BaseModel):
    """Message filtering criteria value object"""
    author: Optional[str] = Field(None, description="Filter by author")
    channel_id: Optional[str] = Field(None, description="Filter by channel")
    platform: Optional[str] = Field(None, description="Filter by platform")
    content_contains: Optional[str] = Field(None, description="Filter by content")
    start_date: Optional[datetime] = Field(None, description="Start date filter")
    end_date: Optional[datetime] = Field(None, description="End date filter")
    limit: int = Field(default=100, description="Maximum messages to return")