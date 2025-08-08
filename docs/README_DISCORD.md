# 🤖 Discord Trading Signal Bot API

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.68+-green.svg)
![Discord](https://img.shields.io/badge/Discord-API-7289da.svg)
![MongoDB](https://img.shields.io/badge/MongoDB-4.0+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**Hệ thống API thu thập và lưu trữ trading signals từ Discord channels tự động**

Dịch vụ tự động thu thập trading signals từ Discord channels, lưu trữ vào MongoDB và cung cấp RESTful API để truy cập dữ liệu.

## 📋 Tính năng chính

### 🔄 Tự động thu thập
- ✅ **Auto Message Fetching** - Thu thập messages từ Discord channel mỗi phút
- ✅ **Smart Filtering** - Lọc messages từ user cụ thể
- ✅ **Message Grouping** - Nhóm messages theo thời gian (5 phút)
- ✅ **Duplicate Prevention** - Tránh lưu trữ messages trùng lặp

### 💾 Quản lý dữ liệu
- ✅ **MongoDB Storage** - Lưu trữ hiệu quả với indexing
- ✅ **Message Deduplication** - Kiểm tra và tránh duplicate data  
- ✅ **Structured Data** - Dữ liệu có cấu trúc với Pydantic models
- ✅ **Reply Handling** - Xử lý reply messages và attachments

### 📊 API Features
- ✅ **RESTful Endpoints** - API endpoints đầy đủ
- ✅ **Real-time Data** - Truy cập data thời gian thực
- ✅ **Flexible Fetching** - Cấu hình linh hoạt qua API hoặc env
- ✅ **Health Monitoring** - Health check và status monitoring

## 🏗️ Kiến trúc hệ thống

```
Discord Bot API
├── 🌐 FastAPI Application     # Main API server
├── 🔧 Services              # Business logic layer
│   ├── DiscordMessageService # Discord API integration
│   └── DiscordScheduler     # Automated scheduling
├── 📊 Models                # Pydantic data models
│   ├── DiscordMessage       # Individual message structure
│   ├── MessageGroup         # Grouped messages
│   └── DiscordData          # Complete data structure
├── 🛠️ Routers              # API endpoint definitions
└── 💾 MongoDB              # Message storage & indexing
```

## 📦 Cài đặt

### Prerequisites
- **Python 3.8+**
- **MongoDB 4.0+** 
- **Discord User Token** (cho private channels)
- **Discord Channel ID & Target User ID**

### 1. Clone repository
```bash
git clone <repository-url>
cd cross_platform_trader
```

### 2. Tạo virtual environment
```bash
python -m venv env
# Windows
env\Scripts\activate
# Linux/Mac
source env/bin/activate
```

### 3. Cài đặt dependencies
```bash
pip install -r requirements-discord.txt
```

### 4. Cấu hình environment
Tạo file `.env`:
```env
# Discord Settings
DISCORD_USER_TOKEN=your_discord_token
DISCORD_CHANNEL_ID=123456789012345678
TARGET_USER_ID=987654321098765432

# MongoDB Settings
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB=discord_trading_signals
```

### 5. Lấy Discord Token & IDs

#### **Lấy Discord User Token:**
⚠️ **Cảnh báo**: Sử dụng user token vi phạm Discord ToS. Chỉ dùng cho testing.

1. Mở Discord Web (discord.com) trong browser
2. Mở Developer Tools (F12)
3. Network tab → Refresh page
4. Tìm request có `Authorization` header
5. Copy token value (không bao gồm "Bearer")

#### **Lấy Channel ID:**
1. Bật Developer Mode: `Settings → Advanced → Developer Mode`
2. Right-click channel → `Copy ID`

#### **Lấy Target User ID:**
1. Right-click trên user → `Copy ID`

### 6. Chạy ứng dụng
```bash
python main-discord.py
```

Server sẽ chạy tại: `http://localhost:3001`

## 📚 API Documentation

### 🔗 Swagger UI
Truy cập: `http://localhost:3001/docs`

### 📊 API Endpoints Overview

**Tất cả Discord endpoints có prefix `/discord/`**

#### **📨 Message APIs** (`/discord/messages/`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/discord/messages/fetch` | Thu thập messages từ Discord |
| `GET` | `/discord/messages/latest` | Lấy messages mới nhất từ DB |
| `POST` | `/discord/messages/fetch-and-save` | Thu thập và lưu (scheduler) |

#### **💓 Health Check** (`/health`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Kiểm tra trạng thái service |

## 💡 Ví dụ sử dụng

### 1. Thu thập messages từ Discord
```bash
curl -X POST "http://localhost:3001/discord/messages/fetch" \
     -H "Content-Type: application/json" \
     -d '{
       "limit": 50
     }'
```

### 2. Thu thập với custom config
```bash
curl -X POST "http://localhost:3001/discord/messages/fetch" \
     -H "Content-Type: application/json" \
     -d '{
       "discord_token": "your_token",
       "channel_id": "123456789012345678",
       "target_user_id": "987654321098765432",
       "limit": 100
     }'
```

### 3. Lấy messages mới nhất từ database
```bash
curl -X GET "http://localhost:3001/discord/messages/latest?limit=20"
```

### 4. Kiểm tra health status
```bash
curl -X GET "http://localhost:3001/health"
```

### 5. Thu thập và lưu (scheduler endpoint)
```bash
curl -X POST "http://localhost:3001/discord/messages/fetch-and-save" \
     -H "Content-Type: application/json" \
     -d '{}'
```

## 🔄 Auto Scheduler

Hệ thống tự động chạy scheduler mỗi **1 phút** để:

1. **Thu thập messages** từ Discord channel
2. **Lọc messages** từ target user
3. **Kiểm tra duplicates** trong database
4. **Lưu trữ** messages mới vào MongoDB
5. **Log results** và errors

### Cấu hình Scheduler
Scheduler được khởi động tự động khi start service:

```python
# Trong main-discord.py
await discord_scheduler.start_scheduler()  # Auto-start
```

### Monitor Scheduler Status
```bash
# Kiểm tra status qua health endpoint
curl -X GET "http://localhost:3001/health"

# Response example:
{
  "status": "healthy",
  "service": "discord-bot", 
  "discord_scheduler": "running"
}
```

## 📊 Data Structure

### DiscordMessage Model
```json
{
  "message_id": "1234567890123456789",
  "content": "BTC/USDT LONG Entry: 45000",
  "attachments": [
    "https://cdn.discordapp.com/attachments/..."
  ],
  "reply_to": {
    "message_id": "previous_message_id",
    "author": "replied_user",
    "content": "Previous message content",
    "attachments": []
  }
}
```

### MessageGroup Model
```json
{
  "group_id": 1,
  "timestamp": "13/08/2024 15:30",
  "username": "trader_username",
  "messages": [
    // DiscordMessage objects
  ]
}
```

### DiscordData Response
```json
{
  "username": "trader_username",
  "total_messages": 50,
  "exported_count": 10,
  "timespan": {
    "from": "13/08/2024 14:00",
    "to": "13/08/2024 15:30"
  },
  "message_groups": [
    // MessageGroup objects
  ],
  "discord_channel_id": "123456789012345678",
  "target_user_id": "987654321098765432"
}
```

## 🔧 Cấu hình nâng cao

### MongoDB Indexes
Hệ thống tự động tạo indexes để tối ưu performance:

```javascript
// Auto-created indexes
db.trading_signals.createIndex({"messages.message_id": 1})
db.trading_signals.createIndex({"created_at": 1})
db.trading_signals.createIndex({"discord_channel_id": 1, "target_user_id": 1})
db.trading_signals.createIndex({"timestamp": 1})
```

### Environment Variables
```env
# Required
DISCORD_USER_TOKEN=your_token
DISCORD_CHANNEL_ID=channel_id
TARGET_USER_ID=user_id
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB=discord_trading_signals

# Optional
LOG_LEVEL=INFO
SCHEDULER_INTERVAL=1  # minutes
```

## 🚨 Troubleshooting

### ❌ Lỗi: "401 Unauthorized"
**Nguyên nhân:** Discord token không hợp lệ hoặc đã hết hạn

**Giải pháp:**
1. Kiểm tra Discord token trong `.env`
2. Lấy token mới từ Discord web app
3. Đảm bảo token có quyền access channel

### ❌ Lỗi: "No messages found from target user"
**Nguyên nhân:** Target User ID không đúng hoặc user chưa post message

**Giải pháp:**
1. Kiểm tra `TARGET_USER_ID` trong `.env`
2. Đảm bảo user đã post messages trong channel
3. Test với user khác có messages

### ❌ Lỗi: "Failed to connect to MongoDB"
**Nguyên nhân:** MongoDB chưa start hoặc connection string sai

**Giải pháp:**
1. Start MongoDB service:
   ```bash
   # Windows
   net start MongoDB
   
   # Linux/Mac  
   sudo systemctl start mongod
   ```
2. Kiểm tra `MONGODB_URL` trong `.env`
3. Test connection:
   ```bash
   mongo --eval "db.adminCommand('ping')"
   ```

### ❌ Lỗi: "Scheduler not running"
**Nguyên nhân:** Scheduler failed to start

**Giải pháp:**
1. Kiểm tra logs cho error details
2. Restart service:
   ```bash
   python main-discord.py
   ```
3. Verify health endpoint:
   ```bash
   curl -X GET "http://localhost:3001/health"
   ```

## 🔧 Development

### Chạy development mode
```bash
python main-discord.py
# Server auto-reload enabled
```

### Testing với manual fetch
```bash
# Test message fetching
curl -X POST "http://localhost:3001/discord/messages/fetch" \
     -H "Content-Type: application/json" \
     -d '{"limit": 10}'
```

### Database inspection
```bash
# Connect to MongoDB
mongo

# Use database
use discord_trading_signals

# Check collections
show collections

# View recent messages
db.trading_signals.find().sort({created_at: -1}).limit(5)
```

## 📊 Monitoring

### Health Check
```bash
curl -X GET "http://localhost:3001/health"
```

Response format:
```json
{
  "status": "healthy|unhealthy",
  "service": "discord-bot",
  "discord_scheduler": "running|stopped"
}
```

### Logs
- **Application logs**: Console output với timestamps
- **Discord API logs**: Request/response logging  
- **MongoDB logs**: Connection và query logs
- **Scheduler logs**: Job execution và error logs

### Performance Monitoring
- **Message fetch frequency**: 1 phút/lần
- **Duplicate check**: Efficient aggregation pipeline
- **Memory usage**: Monitor cho large message volumes
- **MongoDB performance**: Index usage và query optimization

## 🔒 Security Notes

⚠️ **Quan trọng về Discord User Token:**

1. **ToS Violation**: Sử dụng user token vi phạm Discord Terms of Service
2. **Account Risk**: Account có thể bị suspend/ban
3. **Bot Alternative**: Khuyến khích dùng Discord Bot Token cho production
4. **Private Use Only**: Chỉ dùng cho testing và personal use

### Security Best Practices
- **Environment Variables**: Store tokens trong `.env`, không commit
- **Access Control**: Implement authentication cho production API
- **Rate Limiting**: Respect Discord API rate limits
- **Network Security**: Dùng HTTPS và firewall rules
- **Token Rotation**: Thường xuyên rotate Discord tokens

## 🤝 Contributing

1. Fork repository
2. Tạo feature branch: `git checkout -b feature/discord-enhancement`
3. Commit changes: `git commit -m 'Add Discord feature'`
4. Push to branch: `git push origin feature/discord-enhancement`
5. Open Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

## 📞 Support

- **Email:** your-email@example.com
- **Discord:** Your Discord Server
- **GitHub Issues:** Create issue trong repository

## ⚠️ Legal Disclaimer

1. **Discord ToS**: Việc sử dụng user token có thể vi phạm Discord Terms of Service
2. **Account Risk**: Sử dụng hoàn toàn có trách nhiệm của bạn
3. **Data Privacy**: Đảm bảo tuân thủ privacy policies khi thu thập messages
4. **Trading Risk**: Không chịu trách nhiệm về quyết định trading dựa trên signals

---

**Made with 🤖 for Discord Trading Community**