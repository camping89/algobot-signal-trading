"""Discord platform-specific models and adapters"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from domain.entities.message import Message
from domain.entities.message_group import MessageGroup
from domain.entities.message_filter import MessageFilter

class ReplyToMessage(BaseModel):
    """Discord-specific reply reference"""
    message_id: str
    author: str
    content: str
    attachments: List[str] = []

class DiscordMessage(BaseModel):
    """Discord-specific message model with platform details"""
    message_id: str
    content: str
    attachments: List[str] = []
    reply_to: Optional[ReplyToMessage] = None
    embeds: List[dict] = []
    reactions: List[dict] = []

class DiscordMessageGroup(BaseModel):
    """Discord-specific message grouping"""
    group_id: int
    timestamp: str
    username: str
    messages: List[DiscordMessage] = []

class DiscordData(BaseModel):
    """Discord export data structure"""
    username: str
    total_messages: int
    exported_count: int
    timespan: dict
    message_groups: List[DiscordMessageGroup] = []
    created_at: datetime = datetime.now()
    discord_channel_id: str
    target_user_id: str

class DiscordFetchRequest(BaseModel):
    """Discord-specific fetch request"""
    discord_token: Optional[str] = None
    channel_id: Optional[str] = None
    target_user_id: Optional[str] = None
    limit: int = 100

class DiscordMessageAdapter:
    """Adapter to convert between Discord and domain models"""
    
    @staticmethod
    def to_domain_message(discord_message: DiscordMessage, author: str, channel_id: str, timestamp: datetime) -> Message:
        """Convert Discord message to domain Message"""
        return Message(
            message_id=discord_message.message_id,
            content=discord_message.content,
            author=author,
            timestamp=timestamp,
            platform="discord",
            channel_id=channel_id
        )
    
    @staticmethod
    def to_domain_group(discord_group: DiscordMessageGroup, channel_id: str) -> MessageGroup:
        """Convert Discord message group to domain MessageGroup"""
        domain_messages = [
            DiscordMessageAdapter.to_domain_message(
                msg, 
                discord_group.username, 
                channel_id, 
                datetime.fromisoformat(discord_group.timestamp)
            ) for msg in discord_group.messages
        ]
        
        return MessageGroup(
            group_id=str(discord_group.group_id),
            author=discord_group.username,
            timestamp=datetime.fromisoformat(discord_group.timestamp),
            platform="discord",
            channel_id=channel_id,
            messages=domain_messages
        )
    
    @staticmethod
    def from_domain_filter(domain_filter: MessageFilter) -> DiscordFetchRequest:
        """Convert domain MessageFilter to Discord fetch request"""
        return DiscordFetchRequest(
            channel_id=domain_filter.channel_id,
            limit=domain_filter.limit
        )