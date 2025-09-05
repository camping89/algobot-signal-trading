"""Discord platform adapters"""
from datetime import datetime
from domain.entities.message import Message
from domain.entities.message_group import MessageGroup
from domain.entities.message_filter import MessageFilter
from .discord_message import DiscordMessage
from .discord_message_group import DiscordMessageGroup
from .discord_fetch_request import DiscordFetchRequest


class DiscordMessageAdapter:
    @staticmethod
    def to_domain_message(discord_message: DiscordMessage, author: str, channel_id: str, timestamp: datetime) -> Message:
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
        return DiscordFetchRequest(
            channel_id=domain_filter.channel_id,
            limit=domain_filter.limit
        )