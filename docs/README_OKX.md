# 🚀 OKX Trading API Service

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.68+-green.svg)
![OKX](https://img.shields.io/badge/OKX-API-blue.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**Dịch vụ API giao dịch hoàn chỉnh cho sàn OKX với trading, algo orders và quản lý tài khoản**

Hệ thống cung cấp RESTful API để thực hiện giao dịch, algo trading, quản lý positions và theo dõi thị trường trên sàn OKX.

## 📋 Tính năng chính

### 🎯 Trading Operations
- ✅ **Spot Trading** - Giao dịch spot với market/limit orders
- ✅ **Futures Trading** - Giao dịch futures với đòn bẩy
- ✅ **Order Management** - Tạo, hủy, sửa orders
- ✅ **Position Management** - Quản lý positions, close positions
- ✅ **Margin Trading** - Giao dịch ký quỹ cross/isolated

### 🤖 Algorithmic Trading
- ✅ **Take Profit/Stop Loss** - TP/SL orders tự động
- ✅ **Trigger Orders** - Orders kích hoạt theo điều kiện
- ✅ **Trailing Stop** - Trailing stop loss
- ✅ **Iceberg Orders** - Chia nhỏ orders để ẩn volume
- ✅ **TWAP Orders** - Time-weighted average price orders

### 📊 Market Data & Analysis
- ✅ **Real-time Prices** - Giá thời gian thực
- ✅ **Orderbook Data** - Dữ liệu sổ lệnh
- ✅ **OHLCV Data** - Dữ liệu nến K-line
- ✅ **24h Ticker** - Thông tin ticker 24h
- ✅ **Market Statistics** - Thống kê thị trường

### 👤 Account Management
- ✅ **Balance Information** - Thông tin số dư tài khoản
- ✅ **Position Tracking** - Theo dõi positions
- ✅ **Trade History** - Lịch sử giao dịch
- ✅ **Asset Transfer** - Chuyển asset giữa các account

## 🏗️ Kiến trúc hệ thống

```
OKX Trading API
├── 🌐 FastAPI Application     # Main API server
├── 🔧 Services              # Business logic layer
│   ├── OKXBaseService        # Connection & authentication
│   ├── OKXTradingService     # Spot/Futures trading
│   ├── OKXAlgoService        # Algorithmic trading
│   ├── OKXMarketService      # Market data
│   └── OKXAccountService     # Account management
├── 📊 Models                # Pydantic data models
│   ├── Trade Models          # Trading requests/responses
│   ├── Algo Models           # Algo trading models
│   ├── Market Models         # Market data models
│   └── Account Models        # Account info models
├── 🛠️ Routers              # API endpoint definitions
└── 🔗 OKX REST API         # Official OKX API integration
```

## 📦 Cài đặt

### Prerequisites
- **Python 3.8+**
- **OKX Account** với API access
- **OKX API Key, Secret & Passphrase**

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
pip install -r requirements-trading.txt
```

### 4. Cấu hình OKX API
Tạo file `.env`:
```env
# OKX API Settings
OKX_API_KEY=your_api_key
OKX_SECRET_KEY=your_secret_key
OKX_PASSPHRASE=your_passphrase
OKX_IS_SANDBOX=true  # true for demo, false for live

# MongoDB Settings (cho signals)
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB=okx_trading

# Optional: Notification Settings
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
DISCORD_WEBHOOK_URL=your_discord_webhook
```

### 5. Lấy OKX API Credentials

#### **Tạo API Key trên OKX:**
1. Đăng nhập OKX → **Profile** → **API Management**
2. **Create API Key**
3. Đặt tên API Key và permissions:
   - ✅ **Read**: Market data, account info
   - ✅ **Trade**: Spot & futures trading
   - ⚠️ **Withdraw**: (Không khuyến khích cho trading bot)
4. Whitelist IP addresses (khuyến khích cho security)
5. Lưu **API Key**, **Secret Key**, **Passphrase**

#### **Sandbox vs Live Trading:**
- **Sandbox (Demo)**: `OKX_IS_SANDBOX=true` - Dùng cho test
- **Live Trading**: `OKX_IS_SANDBOX=false` - Trading thật với tiền thật

### 6. Chạy ứng dụng
```bash
python main-trading.py
```

Server sẽ chạy tại: `http://localhost:3002`

## 📚 API Documentation

### 🔗 Swagger UI
Truy cập: `http://localhost:3002/docs`

### 📊 API Endpoints Overview

**Tất cả OKX endpoints có prefix `/okx/`**

#### **🎯 Trading APIs** (`/okx/trading/`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/okx/trading/place-order` | Đặt order (market/limit) |
| `GET` | `/okx/trading/orders` | Lấy danh sách orders |
| `DELETE` | `/okx/trading/cancel-order` | Hủy order |
| `PUT` | `/okx/trading/modify-order` | Sửa order |
| `POST` | `/okx/trading/close-position` | Đóng position |
| `GET` | `/okx/trading/positions` | Lấy danh sách positions |
| `GET` | `/okx/trading/fills` | Lịch sử fills |

#### **🤖 Algo Trading APIs** (`/okx/algo-trading/`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/okx/algo-trading/place-tp-sl` | TP/SL order |
| `POST` | `/okx/algo-trading/place-trigger` | Trigger order |
| `POST` | `/okx/algo-trading/place-trailing-stop` | Trailing stop order |
| `POST` | `/okx/algo-trading/place-iceberg` | Iceberg order |
| `POST` | `/okx/algo-trading/place-twap` | TWAP order |
| `GET` | `/okx/algo-trading/orders` | Lấy algo orders |
| `DELETE` | `/okx/algo-trading/cancel-order` | Hủy algo order |

#### **📈 Market Data APIs** (`/okx/market/`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/okx/market/instruments` | Danh sách instruments |
| `GET` | `/okx/market/ticker/{instId}` | Ticker data |
| `GET` | `/okx/market/tickers` | All tickers |
| `GET` | `/okx/market/orderbook/{instId}` | Order book |
| `GET` | `/okx/market/candles/{instId}` | OHLCV data |
| `GET` | `/okx/market/trades/{instId}` | Trade history |

#### **👤 Account APIs** (`/okx/account/`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/okx/account/balance` | Account balance |
| `GET` | `/okx/account/positions` | Account positions |
| `GET` | `/okx/account/bills` | Account bills |
| `GET` | `/okx/account/config` | Account configuration |

## 💡 Ví dụ sử dụng

### 1. Đặt Market Order (Spot)
```bash
curl -X POST "http://localhost:3002/okx/trading/place-order" \
     -H "Content-Type: application/json" \
     -d '{
       "inst_id": "BTC-USDT",
       "td_mode": "cash",
       "side": "buy",
       "ord_type": "market",
       "sz": "100"
     }'
```

### 2. Đặt Limit Order (Futures)
```bash
curl -X POST "http://localhost:3002/okx/trading/place-order" \
     -H "Content-Type: application/json" \
     -d '{
       "inst_id": "BTC-USDT-SWAP",
       "td_mode": "cross",
       "side": "buy",
       "ord_type": "limit",
       "sz": "1",
       "px": "45000"
     }'
```

### 3. Đặt TP/SL Order
```bash
curl -X POST "http://localhost:3002/okx/algo-trading/place-tp-sl" \
     -H "Content-Type: application/json" \
     -d '{
       "inst_id": "BTC-USDT-SWAP",
       "td_mode": "cross",
       "side": "buy",
       "sz": "1",
       "tp_trigger_px": "50000",
       "tp_ord_px": "-1",
       "sl_trigger_px": "40000",
       "sl_ord_px": "-1"
     }'
```

### 4. Lấy Account Balance
```bash
curl -X GET "http://localhost:3002/okx/account/balance"
```

### 5. Lấy Market Data
```bash
# Ticker data
curl -X GET "http://localhost:3002/okx/market/ticker/BTC-USDT"

# OHLCV data
curl -X GET "http://localhost:3002/okx/market/candles/BTC-USDT?bar=1H&limit=100"

# Order book
curl -X GET "http://localhost:3002/okx/market/orderbook/BTC-USDT?sz=20"
```

### 6. Quản lý Orders
```bash
# Lấy active orders
curl -X GET "http://localhost:3002/okx/trading/orders?inst_type=SPOT"

# Hủy order
curl -X DELETE "http://localhost:3002/okx/trading/cancel-order" \
     -H "Content-Type: application/json" \
     -d '{
       "inst_id": "BTC-USDT",
       "ord_id": "123456789"
     }'
```

## 🔧 Cấu hình Trading

### Trading Modes (td_mode)
- **cash**: Spot trading (không đòn bẩy)
- **cross**: Cross margin (đòn bẩy chung)
- **isolated**: Isolated margin (đòn bẩy riêng biệt)

### Order Types (ord_type)
- **market**: Market order (thực hiện ngay)
- **limit**: Limit order (giá cố định)
- **post_only**: Post-only order (maker only)
- **fok**: Fill or Kill
- **ioc**: Immediate or Cancel

### Instrument Types
```bash
# Spot Trading
BTC-USDT, ETH-USDT, BNB-USDT

# Perpetual Futures
BTC-USDT-SWAP, ETH-USDT-SWAP

# Quarterly Futures  
BTC-USDT-240329, ETH-USDT-240329

# Options
BTC-USD-240329-50000-C
```

## 🤖 Algorithmic Trading Examples

### 1. Take Profit + Stop Loss
```json
{
  "inst_id": "BTC-USDT-SWAP",
  "td_mode": "cross",
  "side": "buy",
  "sz": "0.1",
  "tp_trigger_px": "48000",    // Take profit at 48k
  "tp_ord_px": "-1",           // Market price
  "sl_trigger_px": "42000",    // Stop loss at 42k  
  "sl_ord_px": "-1"            // Market price
}
```

### 2. Trailing Stop Order
```json
{
  "inst_id": "ETH-USDT-SWAP",
  "td_mode": "cross",
  "side": "sell",
  "sz": "1", 
  "callback_ratio": "0.05",    // 5% trailing
  "active_px": "3200"          // Activate when price >= 3200
}
```

### 3. Iceberg Order (Large Volume)
```json
{
  "inst_id": "BTC-USDT",
  "td_mode": "cash",
  "side": "buy",
  "ord_type": "limit",
  "sz": "10",                  // Total 10 BTC
  "px": "45000",
  "sz_limit": "1"              // Show only 1 BTC at a time
}
```

## 🚨 Troubleshooting

### ❌ Lỗi: "Invalid signature"
**Nguyên nhân:** API credentials không đúng hoặc signature sai

**Giải pháp:**
1. Kiểm tra **API Key**, **Secret Key**, **Passphrase** trong `.env`
2. Đảm bảo API Key có quyền **Trade** permission
3. Kiểm tra system time sync (quan trọng cho signature)
4. Verify API endpoint URL (sandbox vs live)

### ❌ Lỗi: "Insufficient balance"
**Nguyên nhân:** Không đủ số dư để thực hiện giao dịch

**Giải pháp:**
1. Kiểm tra balance:
   ```bash
   curl -X GET "http://localhost:3002/okx/account/balance"
   ```
2. Đảm bảo có đủ balance trong trading account
3. Chuyển funds từ funding account sang trading account

### ❌ Lỗi: "Order size too small"
**Nguyên nhân:** Kích thước order nhỏ hơn minimum requirement

**Giải pháp:**
1. Kiểm tra minimum order size cho instrument:
   ```bash
   curl -X GET "http://localhost:3002/okx/market/instruments?instType=SPOT"
   ```
2. Tăng order size phù hợp với `minSz` requirement

### ❌ Lỗi: "Position not found"
**Nguyên nhân:** Không tìm thấy position để close

**Giải pháp:**
1. Kiểm tra active positions:
   ```bash
   curl -X GET "http://localhost:3002/okx/trading/positions"
   ```
2. Đảm bảo position ID và inst_id chính xác
3. Verify position vẫn còn open (chưa bị close)

## 🔒 Security & Best Practices

### API Security
- **IP Whitelist**: Chỉ allow specific IP addresses
- **API Permissions**: Chỉ cấp permissions cần thiết (Read, Trade)
- **Environment Variables**: Store credentials trong `.env`, không hardcode
- **Regular Rotation**: Định kỳ rotate API keys

### Trading Risk Management
- **Position Sizing**: Không risk quá 2-5% mỗi trade
- **Stop Loss**: Luôn set stop loss cho mọi position
- **Diversification**: Không all-in vào 1 instrument
- **Testing**: Test trên sandbox trước khi live trading

### Production Considerations
```bash
# Production deployment
gunicorn main-trading:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:3002 \
  --access-log-format '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'
```

## 📊 Monitoring & Health Check

### Health Check
```bash
curl -X GET "http://localhost:3002/health"
```

Response:
```json
{
  "status": "healthy",
  "service": "trading", 
  "services": {
    "mt5": "disconnected",
    "okx": "connected"
  }
}
```

### Performance Monitoring
- **API Rate Limits**: Monitor OKX rate limits
- **Connection Health**: Check WebSocket connections
- **Error Rates**: Track failed requests
- **Latency**: Monitor response times

## 🔧 Development

### Development Mode
```bash
python main-trading.py
```

### Testing với Sandbox
```env
# .env for testing
OKX_IS_SANDBOX=true
OKX_API_KEY=sandbox_api_key
OKX_SECRET_KEY=sandbox_secret_key  
OKX_PASSPHRASE=sandbox_passphrase
```

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python main-trading.py
```

## 🤝 Contributing

1. Fork repository
2. Tạo feature branch: `git checkout -b feature/okx-enhancement`
3. Commit changes: `git commit -m 'Add OKX feature'`
4. Push to branch: `git push origin feature/okx-enhancement`
5. Open Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

## 📞 Support & Resources

- **OKX API Docs**: https://www.okx.com/docs-v5/en/
- **Email**: your-email@example.com
- **GitHub Issues**: Create issue trong repository

### Useful Links
- **OKX API Reference**: https://www.okx.com/docs-v5/en/#order-book-trading-trade-post-place-order
- **OKX Trading Rules**: https://www.okx.com/docs-v5/en/#trading-rules
- **OKX WebSocket**: https://www.okx.com/docs-v5/en/#websocket-api
- **OKX SDKs**: https://github.com/okx/okx-python-sdk

## ⚠️ Trading Disclaimer

1. **High Risk**: Cryptocurrency trading có rủi ro cao, có thể mất toàn bộ tiền đầu tư
2. **No Financial Advice**: API này chỉ là tool, không phải lời khuyên tài chính
3. **User Responsibility**: Sử dụng hoàn toàn có trách nhiệm của người dùng
4. **Testing First**: Luôn test trên sandbox trước khi live trading
5. **Risk Management**: Implement proper risk management và position sizing

---

**Made with ⚡ for OKX Trading Community**