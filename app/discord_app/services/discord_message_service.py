import requests
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient
from app.discord_app.config import discord_settings
from app.discord_app.models.message import (
    DiscordData, MessageGroup, DiscordMessage, ReplyToMessage, DiscordFetchRequest
)


class DiscordMessageService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.mongo_client: Optional[AsyncIOMotorClient] = None
        self.db = None
        
    async def initialize_db(self):
        """Initialize MongoDB connection and create indexes"""
        try:
            self.mongo_client = AsyncIOMotorClient(discord_settings.MONGODB_URL)
            self.db = self.mongo_client[discord_settings.MONGODB_DB]
            # Test connection
            await self.mongo_client.admin.command('ping')
            
            # Create index on message IDs for faster duplicate checking
            collection = self.db.trading_signals
            await collection.create_index("messages.message_id")
            await collection.create_index("created_at")
            await collection.create_index([("discord_channel_id", 1), ("target_user_id", 1)])
            await collection.create_index("timestamp")
            
            self.logger.info("Connected to MongoDB successfully and created indexes")
        except Exception as e:
            self.logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise
    
    async def fetch_discord_messages(self, request: DiscordFetchRequest) -> Optional[DiscordData]:
        """Fetch messages from Discord channel"""
        try:
            # Use provided values or fall back to env defaults
            token = request.discord_token or discord_settings.DISCORD_USER_TOKEN
            channel_id = request.channel_id or discord_settings.DISCORD_CHANNEL_ID
            target_user_id = request.target_user_id or discord_settings.TARGET_USER_ID
            
            if not all([token, channel_id, target_user_id]):
                raise ValueError("Missing required Discord credentials")
            
            headers = {
                "Authorization": token,
                "User-Agent": "Mozilla/5.0",
            }
            
            url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
            params = {"limit": request.limit}
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code != 200:
                self.logger.error(f"Discord API request failed: {response.status_code}")
                self.logger.error(response.text)
                return None
                
            messages = response.json()
            self.logger.info(f"Fetched {len(messages)} messages from Discord")
            
            # Filter messages from target user
            user_messages = [
                msg for msg in messages if msg["author"]["id"] == target_user_id
            ]
            
            if not user_messages:
                self.logger.warning("No messages found from target user")
                return None
            
            # Sort by timestamp (newest first)
            user_messages.sort(key=lambda x: x["timestamp"], reverse=True)
            
            # Take top 10 messages
            top_10_messages = user_messages[:10]
            
            # Group messages by time (within 5 minutes)
            message_groups = self._group_messages_by_time(top_10_messages)
            
            # Create Discord data object
            discord_data = DiscordData(
                username=user_messages[0]["author"]["username"],
                total_messages=len(user_messages),
                exported_count=len(top_10_messages),
                timespan={
                    "from": datetime.fromisoformat(top_10_messages[-1]["timestamp"].replace("Z", "+00:00")).strftime("%d/%m/%Y %H:%M"),
                    "to": datetime.fromisoformat(top_10_messages[0]["timestamp"].replace("Z", "+00:00")).strftime("%d/%m/%Y %H:%M")
                },
                message_groups=message_groups,
                discord_channel_id=channel_id,
                target_user_id=target_user_id
            )
            
            return discord_data
            
        except Exception as e:
            self.logger.error(f"Error fetching Discord messages: {str(e)}")
            return None
    
    def _group_messages_by_time(self, messages: List[Dict[str, Any]]) -> List[MessageGroup]:
        """Group messages that are sent within 5 minutes of each other"""
        message_groups = []
        current_group = []
        
        for i, msg in enumerate(messages):
            if i == 0:
                current_group = [msg]
            else:
                current_timestamp = datetime.fromisoformat(msg["timestamp"].replace("Z", "+00:00"))
                last_timestamp = datetime.fromisoformat(current_group[-1]["timestamp"].replace("Z", "+00:00"))
                time_diff = abs((last_timestamp - current_timestamp).total_seconds() / 60)
                
                if time_diff <= 5:  # Within 5 minutes
                    current_group.append(msg)
                else:
                    message_groups.append(self._create_message_group(len(message_groups) + 1, current_group))
                    current_group = [msg]
        
        if current_group:
            message_groups.append(self._create_message_group(len(message_groups) + 1, current_group))
        
        return message_groups
    
    def _create_message_group(self, group_id: int, group_messages: List[Dict[str, Any]]) -> MessageGroup:
        """Create a MessageGroup from raw Discord messages"""
        first_msg = group_messages[0]
        timestamp_str = first_msg["timestamp"]
        timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        formatted_time = timestamp.strftime("%d/%m/%Y %H:%M")
        username = first_msg["author"]["username"]
        
        discord_messages = []
        for msg in group_messages:
            content = msg.get("content", "").strip()
            
            # If content is empty, try to get from embeds
            if not content and msg.get("embeds"):
                for emb in msg["embeds"]:
                    if emb.get("description"):
                        content = emb["description"]
                        break
                    elif emb.get("title"):
                        content = emb["title"]
                        break
            
            # Handle attachments
            attachments = []
            if msg.get("attachments"):
                attachments = [att.get("url") for att in msg["attachments"] if att.get("url")]
            
            # Handle reply
            reply_to = None
            if msg.get("message_reference") and msg.get("referenced_message"):
                replied_msg = msg["referenced_message"]
                replied_content = replied_msg.get("content", "").strip()
                replied_author = replied_msg["author"]["username"]
                replied_attachments = []
                if replied_msg.get("attachments"):
                    replied_attachments = [att.get("url") for att in replied_msg["attachments"] if att.get("url")]
                
                reply_to = ReplyToMessage(
                    message_id=replied_msg["id"],
                    author=replied_author,
                    content=replied_content,
                    attachments=replied_attachments
                )
            
            discord_message = DiscordMessage(
                message_id=msg["id"],
                content=content,
                attachments=attachments,
                reply_to=reply_to
            )
            discord_messages.append(discord_message)
        
        return MessageGroup(
            group_id=group_id,
            timestamp=formatted_time,
            username=username,
            messages=discord_messages
        )
    
    async def save_to_database(self, discord_data: DiscordData) -> bool:
        """Save each Discord message group as separate document in MongoDB"""
        try:
            if self.db is None:
                await self.initialize_db()
            
            collection = self.db.trading_signals
            
            # Get all message IDs from the new data
            new_message_ids = []
            for group in discord_data.message_groups:
                for message in group.messages:
                    new_message_ids.append(message.message_id)
            
            # Check if any messages already exist in database using aggregation
            pipeline = [
                {"$match": {"messages.message_id": {"$in": new_message_ids}}},
                {"$unwind": "$messages"},
                {"$match": {"messages.message_id": {"$in": new_message_ids}}},
                {"$group": {"_id": None, "existing_ids": {"$addToSet": "$messages.message_id"}}}
            ]
            
            result = await collection.aggregate(pipeline).to_list(1)
            existing_ids = set(result[0]["existing_ids"]) if result else set()
            
            # Process each group and save as separate document
            saved_groups = 0
            new_messages_count = 0
            
            for group in discord_data.message_groups:
                # Filter out existing messages from this group
                filtered_messages = []
                for message in group.messages:
                    if message.message_id not in existing_ids:
                        filtered_messages.append(message)
                        new_messages_count += 1
                
                # Only save groups that have new messages
                if filtered_messages:
                    # Create document for this group
                    group_doc = {
                        "timestamp": group.timestamp,
                        "username": group.username,
                        "messages": [msg.dict() for msg in filtered_messages],
                        "discord_channel_id": discord_data.discord_channel_id,
                        "target_user_id": discord_data.target_user_id,
                        "created_at": datetime.utcnow()
                    }
                    
                    # Insert group as separate document
                    result = await collection.insert_one(group_doc)
                    if result.inserted_id:
                        saved_groups += 1
                        self.logger.info(f"Saved message group with {len(filtered_messages)} messages")
            
            if saved_groups > 0:
                self.logger.info(f"Successfully saved {saved_groups} message groups with {new_messages_count} new messages total")
                return True
            else:
                self.logger.info("No new message groups to save - all messages already exist in database")
                return True
                
        except Exception as e:
            self.logger.error(f"Error saving to database: {str(e)}")
            return False
    
    async def get_latest_messages(self, limit: int = 10) -> List[Dict]:
        """Get latest Discord message groups from database"""
        try:
            if self.db is None:
                await self.initialize_db()
            
            collection = self.db.trading_signals
            cursor = collection.find().sort("created_at", -1).limit(limit)
            
            message_groups = []
            async for doc in cursor:
                # Convert ObjectId to string
                doc["_id"] = str(doc["_id"])
                message_groups.append(doc)
            
            return message_groups
            
        except Exception as e:
            self.logger.error(f"Error fetching message groups from database: {str(e)}")
            return []
    
    async def get_message_count_by_user(self, target_user_id: str) -> int:
        """Get total count of messages for a specific user"""
        try:
            if self.db is None:
                await self.initialize_db()
            
            collection = self.db.trading_signals
            
            # Count total messages for this user
            pipeline = [
                {"$match": {"target_user_id": target_user_id}},
                {"$unwind": "$messages"},
                {"$count": "total_messages"}
            ]
            
            result = await collection.aggregate(pipeline).to_list(1)
            return result[0]["total_messages"] if result else 0
            
        except Exception as e:
            self.logger.error(f"Error getting message count: {str(e)}")
            return 0
    
    async def close_db_connection(self):
        """Close MongoDB connection"""
        if self.mongo_client:
            self.mongo_client.close()
            self.logger.info("MongoDB connection closed")