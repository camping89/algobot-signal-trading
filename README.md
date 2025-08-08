# 🔥 Cross-Platform Trading System

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.68+-green.svg)
![MT5](https://img.shields.io/badge/MetaTrader5-5.0+-orange.svg)
![OKX](https://img.shields.io/badge/OKX-API-blue.svg)
![Discord](https://img.shields.io/badge/Discord-API-7289da.svg)
![MongoDB](https://img.shields.io/badge/MongoDB-4.0+-green.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**Hệ thống trading đa nền tảng với MT5, OKX và Discord Bot tự động**

Một ecosystem hoàn chỉnh cho automated trading, signal collection và market analysis trên nhiều sàn giao dịch.

## 🏗️ Kiến trúc hệ thống

```
Cross-Platform Trading System
├── 🤖 Discord Service (Port 3001)    # Signal collection & monitoring
│   ├── Auto Message Fetching        # Thu thập trading signals  
│   ├── MongoDB Storage               # Lưu trữ signals
│   └── RESTful API                   # Discord message API
│
├── ⚡ Trading Service (Port 3002)     # Multi-platform trading
│   ├── 🚀 MT5 Integration           # MetaTrader 5 trading
│   │   ├── Spot & CFD Trading       # Forex, Gold, Indices
│   │   ├── Risk Management          # Position sizing, SL/TP
│   │   ├── Automation               # Grid, Martingale strategies
│   │   └── Notifications            # Telegram, Discord alerts
│   │
│   └── 💎 OKX Integration           # Cryptocurrency trading
│       ├── Spot & Futures Trading   # Crypto spot & derivatives
│       ├── Algo Trading             # TP/SL, Trailing stops
│       ├── Market Data              # Real-time prices, orderbook
│       └── Account Management       # Balance, positions
│
└── 🐳 Docker Support                # Containerized deployment
    ├── Dockerfile.discord           # Discord service container
    ├── Dockerfile.trading           # Trading service container
    └── docker-compose.yml           # Multi-service orchestration
```

## 🚀 Quick Start

### Option 1: Docker (Recommended)
```bash
# Clone repository
git clone <repository-url>
cd cross_platform_trader

# Configure environment
cp .env.example .env
# Edit .env với credentials của bạn

# Start all services
cd docker
docker-compose up -d

# Check services
curl http://localhost:3001/health  # Discord service
curl http://localhost:3002/health  # Trading service
```

### Option 2: Manual Setup
```bash
# Create virtual environment
python -m venv env

# Activate virtual environment
# Windows
env\Scripts\activate
# Linux/Mac
source env/bin/activate

# Install dependencies
pip install -r requirements/discord.txt
pip install -r requirements/trading.txt

# Configure environment
cp .env.example .env
# Edit .env với credentials của bạn

# Start Discord service
python main-discord.py

# Start Trading service (new terminal)
python main-trading.py
```

## 📚 Documentation

### 📖 Service Documentation
| Service | Port | Documentation | Description |
|---------|------|---------------|-------------|
| 🤖 **Discord Bot** | 3001 | [README_DISCORD.md](docs/README_DISCORD.md) | Signal collection from Discord channels |
| 🚀 **MT5 Trading** | 3002 | [README_MT5.md](docs/README_MT5.md) | MetaTrader 5 automated trading |
| 💎 **OKX Trading** | 3002 | [README_OKX.md](docs/README_OKX.md) | OKX cryptocurrency trading |

### 🌐 API Documentation
- **Discord API**: http://localhost:3001/docs
- **Trading API**: http://localhost:3002/docs

## ⚙️ Environment Configuration

### Required Environment Variables
```env
# Discord Settings
DISCORD_USER_TOKEN=your_discord_token
DISCORD_CHANNEL_ID=123456789012345678
TARGET_USER_ID=987654321098765432

# MT5 Settings
MT5_LOGIN=your_mt5_login
MT5_PASSWORD=your_mt5_password  
MT5_SERVER=your_mt5_server

# OKX Settings
OKX_API_KEY=your_api_key
OKX_SECRET_KEY=your_secret_key
OKX_PASSPHRASE=your_passphrase
OKX_IS_SANDBOX=true

# MongoDB
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB=trading_system

# Notifications (Optional)
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
DISCORD_WEBHOOK_URL=your_discord_webhook
```

## 💡 Use Cases & Examples

### 1. Discord Signal Collection
```bash
# Auto-collect trading signals từ Discord channel
curl -X POST "http://localhost:3001/discord/messages/fetch" \
     -H "Content-Type: application/json" \
     -d '{"limit": 50}'

# Lấy signals đã collect
curl -X GET "http://localhost:3001/discord/messages/latest?limit=10"
```

### 2. MT5 Automated Trading
```bash
# Thực hiện market order
curl -X POST "http://localhost:3002/mt5/trading/market-order" \
     -H "Content-Type: application/json" \
     -d '{
       "symbol": "XAUUSD",
       "order_type": "BUY", 
       "amount": 0.1,
       "stop_loss": 1950,
       "take_profit": 2050
     }'

# Lấy account info
curl -X GET "http://localhost:3002/mt5/account/info"
```

### 3. OKX Crypto Trading
```bash
# Đặt limit order BTC
curl -X POST "http://localhost:3002/okx/trading/place-order" \
     -H "Content-Type: application/json" \
     -d '{
       "inst_id": "BTC-USDT",
       "td_mode": "cash",
       "side": "buy",
       "ord_type": "limit",
       "sz": "0.001",
       "px": "45000"
     }'

# Đặt TP/SL order
curl -X POST "http://localhost:3002/okx/algo-trading/place-tp-sl" \
     -H "Content-Type: application/json" \
     -d '{
       "inst_id": "BTC-USDT-SWAP",
       "td_mode": "cross", 
       "side": "buy",
       "sz": "0.1",
       "tp_trigger_px": "50000",
       "sl_trigger_px": "40000"
     }'
```

## 🔧 Advanced Features

### 🤖 Automated Strategies
- **Grid Trading**: Tự động tạo lưới lệnh
- **Martingale**: Tăng size sau lỗ
- **Signal-based Trading**: Trading theo Discord signals
- **Risk Management**: Auto SL/TP, position sizing

### 📊 Market Analysis
- **Real-time Data**: Prices từ MT5 và OKX
- **Technical Indicators**: Built-in TA indicators
- **Multi-timeframe**: 1m, 5m, 1h, 4h, 1D analysis
- **Cross-platform Arbitrage**: Compare prices across platforms

### 📱 Notifications & Monitoring
- **Telegram Alerts**: Trade notifications
- **Discord Webhooks**: Server updates
- **Health Monitoring**: Service status checks
- **Performance Analytics**: P&L tracking

## 🐳 Docker Deployment

### Development
```bash
cd docker
docker-compose up --build
```

### Production
```bash
cd docker
docker-compose up -d
```

### Individual Services
```bash
cd docker

# Discord service only
docker-compose up discord-bot

# Trading service only  
docker-compose up trading-service
```

## 📊 Monitoring & Health Checks

### Service Status
```bash
# Check all services
curl http://localhost:3001/health && curl http://localhost:3002/health

# Expected responses:
# Discord: {"status": "healthy", "service": "discord-bot", "discord_scheduler": "running"}
# Trading: {"status": "healthy", "service": "trading", "services": {"mt5": "connected", "okx": "connected"}}
```

### Performance Monitoring
- **Discord**: Message fetch rate, duplicate detection
- **MT5**: Connection status, order execution latency
- **OKX**: API rate limits, error rates
- **MongoDB**: Collection sizes, query performance

## 🚨 Common Issues & Solutions

### Discord Service Issues
```bash
# Token expired
# Solution: Update DISCORD_USER_TOKEN in .env

# No messages found
# Solution: Check TARGET_USER_ID and DISCORD_CHANNEL_ID

# MongoDB connection failed
# Solution: Ensure MongoDB is running and MONGODB_URL is correct
```

### Trading Service Issues
```bash
# MT5 connection failed
# Solution: Check MT5 credentials and ensure MT5 terminal is running

# OKX API errors
# Solution: Verify API key permissions and rate limits

# Invalid signatures
# Solution: Check system time sync for API signatures
```

## 🔒 Security Best Practices

### API Security
- **Environment Variables**: Never hardcode credentials
- **IP Whitelisting**: Restrict API access by IP
- **API Permissions**: Minimum required permissions only
- **Regular Rotation**: Rotate API keys monthly

### Trading Security
- **Position Limits**: Set maximum position sizes
- **Stop Losses**: Always use stop losses
- **Diversification**: Don't risk more than 2-5% per trade
- **Testing**: Test on demo accounts first

## 🤝 Contributing

1. Fork repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

## 📞 Support

- **Documentation**: Check service-specific READMEs in `docs/`
- **Issues**: Create GitHub issue với detailed description
- **Email**: your-email@example.com

## ⚠️ Trading Disclaimer

**CẢNH BÁO**: Trading forex, CFDs và cryptocurrency có rủi ro cao. Bạn có thể mất tất cả tiền đầu tư. Hệ thống này chỉ là công cụ hỗ trợ, không phải lời khuyên tài chính. Sử dụng hoàn toàn có trách nhiệm của bạn.

## 📁 Project Structure

```
cross_platform_trader/
├── 📖 README.md                        # Main documentation
├── 📱 main-discord.py                   # Discord service entry point
├── ⚡ main-trading.py                   # Trading service entry point
├── 📁 docs/                            # Documentation
│   ├── 🤖 README_DISCORD.md            # Discord Bot API docs
│   ├── 🚀 README_MT5.md                # MT5 Trading docs
│   └── 💎 README_OKX.md                # OKX Trading docs
├── 🐳 docker/                          # Docker configuration
│   ├── Dockerfile.discord              # Discord service container
│   ├── Dockerfile.trading              # Trading service container
│   └── docker-compose.yml              # Multi-service orchestration
├── 📦 requirements/                     # Python dependencies
│   ├── discord.txt                     # Discord service deps
│   └── trading.txt                     # Trading service deps
├── 📂 app/                             # Application source code
│   ├── 🤖 discord_app/                 # Discord service
│   │   ├── config.py                   # Discord configuration
│   │   ├── models/                     # Discord data models
│   │   ├── routers/                    # Discord API routes
│   │   └── services/                   # Discord business logic
│   ├── ⚡ trading_app/                 # Trading service
│   │   ├── config.py                   # Trading configuration
│   │   ├── models/                     # Trading data models
│   │   │   ├── mt5/                    # MT5 specific models
│   │   │   └── okx/                    # OKX specific models
│   │   ├── routers/                    # Trading API routes
│   │   │   ├── mt5/                    # MT5 endpoints
│   │   │   └── okx/                    # OKX endpoints
│   │   └── services/                   # Trading business logic
│   │       ├── mt5/                    # MT5 services
│   │       └── okx/                    # OKX services
│   └── 🔄 shared/                      # Shared utilities
│       └── utils/                      # Common helper functions
└── 📄 LICENSE                          # MIT License
```

---

**Made with ❤️ for the Trading Community**

*Empowering traders with automated, cross-platform trading solutions.*