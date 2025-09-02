# Debugging and Port Configuration Guide

## Service Ports

### Default Port Configuration

The application uses the following ports in development:

#### Application Services
- **Discord Service**: http://localhost:3000
  - API endpoint: `http://localhost:3000`
  - Health check: `http://localhost:3000/health`
  - API Documentation: `http://localhost:3000/docs`
  - OpenAPI spec: `http://localhost:3000/openapi.json`

- **Trading Service**: http://localhost:3010
  - API endpoint: `http://localhost:3010`
  - Health check: `http://localhost:3010/health`
  - API Documentation: `http://localhost:3010/docs`
  - OpenAPI spec: `http://localhost:3010/openapi.json`

#### Database Services
- **MongoDB**: `localhost:3099`
  - Connection string: `mongodb://localhost:3099/algobot_signal_trading`
  - Default database: `algobot_signal_trading`

- **Redis**: `localhost:3098`
  - Connection string: `redis://localhost:3098`
  - Default database: 0

### Port Conflict Resolution

If you encounter port conflicts, you can modify the ports in:

1. **Docker Compose** (`docker-compose.dev.yml`):
```yaml
services:
  discord:
    ports:
      - "3000:3000"  # Change the first number to use a different external port
  trading:
    ports:
      - "3010:3010"  # Change the first number to use a different external port
```

2. **Local Development** (when running without Docker):
```bash
# Discord service on different port
python -m uvicorn main:app --host 0.0.0.0 --port 3001 --reload

# Trading service on different port
python -m uvicorn main:app --host 0.0.0.0 --port 3011 --reload
```

3. **Environment Variables** (`.env` file):
```env
# Service ports
DISCORD_SERVICE_PORT=3000
TRADING_SERVICE_PORT=3010

# Database ports
MONGODB_PORT=3099
REDIS_PORT=3098
```

## Debugging Setup

### IDE Configuration

#### VS Code

1. **Python Debugging Configuration** (`.vscode/launch.json`):
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Discord Service",
            "type": "python",
            "request": "launch",
            "module": "uvicorn",
            "args": [
                "main:app",
                "--host", "0.0.0.0",
                "--port", "3000",
                "--reload"
            ],
            "cwd": "${workspaceFolder}/app/discord",
            "env": {
                "PYTHONPATH": "${workspaceFolder}"
            }
        },
        {
            "name": "Trading Service",
            "type": "python",
            "request": "launch",
            "module": "uvicorn",
            "args": [
                "main:app",
                "--host", "0.0.0.0",
                "--port", "3010",
                "--reload"
            ],
            "cwd": "${workspaceFolder}/app/trading",
            "env": {
                "PYTHONPATH": "${workspaceFolder}"
            }
        }
    ]
}
```

#### PyCharm

1. **Run Configuration for Discord Service**:
   - Script: `-m uvicorn`
   - Parameters: `main:app --host 0.0.0.0 --port 3000 --reload`
   - Working directory: `app/discord`
   - Environment variables: Load from `.env`

2. **Run Configuration for Trading Service**:
   - Script: `-m uvicorn`
   - Parameters: `main:app --host 0.0.0.0 --port 3010 --reload`
   - Working directory: `app/trading`
   - Environment variables: Load from `.env`

### Docker Debugging

#### View Container Logs
```bash
# All services
docker-compose -f docker-compose.dev.yml logs -f

# Specific service
docker-compose -f docker-compose.dev.yml logs -f discord
docker-compose -f docker-compose.dev.yml logs -f trading
docker-compose -f docker-compose.dev.yml logs -f mongodb
docker-compose -f docker-compose.dev.yml logs -f redis

# Last 100 lines
docker-compose -f docker-compose.dev.yml logs --tail=100 discord
```

#### Access Container Shell
```bash
# Discord service container
docker-compose -f docker-compose.dev.yml exec discord /bin/bash

# Trading service container
docker-compose -f docker-compose.dev.yml exec trading /bin/bash

# MongoDB container
docker-compose -f docker-compose.dev.yml exec mongodb mongosh
```

#### Container Status and Health
```bash
# Check container status
docker-compose -f docker-compose.dev.yml ps

# Inspect container details
docker inspect algobot-signal-trading_discord_1

# Check resource usage
docker stats
```

### Remote Debugging

#### Attach Debugger to Docker Container

1. **Update docker-compose.dev.yml** to expose debug port:
```yaml
services:
  discord:
    ports:
      - "3000:3000"
      - "5678:5678"  # Debug port
    environment:
      - DEBUG_MODE=true
```

2. **Add debugpy to requirements**:
```txt
debugpy==1.8.0
```

3. **Add debug configuration in main.py**:
```python
import os
if os.getenv("DEBUG_MODE") == "true":
    import debugpy
    debugpy.listen(("0.0.0.0", 5678))
    print("⏸ Debugger listening on port 5678")
    # debugpy.wait_for_client()  # Uncomment to wait for debugger attach
```

4. **VS Code Remote Attach Configuration**:
```json
{
    "name": "Python: Remote Attach",
    "type": "python",
    "request": "attach",
    "connect": {
        "host": "localhost",
        "port": 5678
    },
    "pathMappings": [
        {
            "localRoot": "${workspaceFolder}",
            "remoteRoot": "/app"
        }
    ]
}
```

### Logging and Monitoring

#### Log Levels
Configure log level via environment variable:
```env
LOG_LEVEL=DEBUG  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
```

#### Structured Logging
The application uses structured logging with contextual information:
```python
import logging
logger = logging.getLogger(__name__)

# Example usage
logger.debug("Processing signal", extra={
    "signal_id": signal.id,
    "symbol": signal.symbol,
    "action": signal.action
})
```

#### Log Files
When running locally, logs are also written to files:
- Discord service: `app/discord/logs/discord.log`
- Trading service: `app/trading/logs/trading.log`

### Common Debugging Commands

#### Health Checks
```bash
# Check service health
curl http://localhost:3000/health
curl http://localhost:3010/health

# Verbose output
curl -v http://localhost:3000/health
```

#### API Testing
```bash
# Test with curl
curl -X GET http://localhost:3000/api/messages

# Test with httpie
http GET localhost:3000/api/messages

# Test with specific headers
curl -H "Content-Type: application/json" \
     -X POST http://localhost:3010/api/signals \
     -d '{"symbol":"BTC-USDT","action":"BUY"}'
```

#### Database Debugging

**MongoDB Commands**:
```bash
# Connect to MongoDB
docker-compose -f docker-compose.dev.yml exec mongodb mongosh

# In MongoDB shell
use algobot_signal_trading
show collections
db.signals.find().pretty()
db.signals.countDocuments()
```

**Redis Commands**:
```bash
# Connect to Redis
docker-compose -f docker-compose.dev.yml exec redis redis-cli

# In Redis CLI
KEYS *
GET key_name
MONITOR  # Watch all commands in real-time
```

### Performance Profiling

#### Using cProfile
```python
import cProfile
import pstats

def profile_function():
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Your code here
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)  # Top 10 functions
```

#### Memory Profiling
```bash
# Install memory profiler
pip install memory-profiler

# Run with memory profiling
python -m memory_profiler main.py
```

### Troubleshooting Common Issues

#### Port Already in Use
```bash
# Find process using port
lsof -i :3000  # macOS/Linux
netstat -ano | findstr :3000  # Windows

# Kill process
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows
```

#### Container Won't Start
```bash
# Check logs
docker-compose -f docker-compose.dev.yml logs discord

# Rebuild container
docker-compose -f docker-compose.dev.yml build --no-cache discord
docker-compose -f docker-compose.dev.yml up discord
```

#### Database Connection Issues
```bash
# Test MongoDB connection
mongosh --host localhost --port 3099

# Test Redis connection
redis-cli -h localhost -p 3098 ping
```

#### Module Import Errors
```bash
# Verify virtual environment
which python
pip list

# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

### Debug Environment Variables

Add these to your `.env` for enhanced debugging:
```env
# Debug settings
DEBUG_MODE=true
LOG_LEVEL=DEBUG
PYTHONUNBUFFERED=1  # Ensure stdout/stderr are unbuffered

# Development settings
RELOAD=true  # Auto-reload on code changes
WORKERS=1    # Single worker for debugging

# Tracing
ENABLE_TRACING=true
TRACE_SAMPLE_RATE=1.0
```

---

**Note**: Remember to disable debug mode and use appropriate log levels in production environments for security and performance reasons.