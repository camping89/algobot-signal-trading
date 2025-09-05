"""Discord reply reference model"""
from pydantic import BaseModel
from typing import List


class ReplyToMessage(BaseModel):
    message_id: str
    author: str
    content: str
    attachments: List[str] = []
