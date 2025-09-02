# OKX Signal Trading - Local Development Setup Guide

This guide will help you set up and run the OKX Trading System locally on your machine.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Environment Configuration](#environment-configuration)
- [Installation](#installation)
- [Database Setup](#database-setup)
- [Running the Application](#running-the-application)
- [Testing](#testing)
- [Project Architecture](#project-architecture)

## Prerequisites

### Required Software
- **Python 3.12+** - The project requires Python 3.12 or higher
- **Docker & Docker Compose** - For containerized development (recommended)
- **Git** - For version control

## Environment Configuration

Copy the example environment file:
```bash
cp .env.example .env
```


## Installation

### Docker Development Setup

This method sets up the entire stack with one command, including all services and databases, following production-style deployment.

#### 1. Start All Services
```bash
docker-compose -f docker-compose.dev.yml up -d
```

#### 2. View Logs
```bash
# View all service logs
docker-compose -f docker-compose.dev.yml logs -f

# View specific service logs
docker-compose -f docker-compose.dev.yml logs -f discord
docker-compose -f docker-compose.dev.yml logs -f trading
```

#### 3. Stop Services
```bash
docker-compose -f docker-compose.dev.yml down
```

#### 4. Rebuild Services (after code changes)
```bash
docker-compose -f docker-compose.dev.yml up --build
```

## Database Setup

### MongoDB Collections
The application will automatically create the necessary collections on first run:
- `messages` - Discord messages
- `signals` - Trading signals
- `trades` - Trade records
- `positions` - Position tracking

### Initial Data (Optional)
No initial data setup is required. The system will create collections and indexes automatically.

## Running the Application

### Service Endpoints

Once running, the services will be available on their configured ports. See `debug.md` for detailed port configuration and debugging setup.

### Verification Steps

1. **Check Service Health:**
Use the health check endpoints for each service (see `debug.md` for ports and debugging)

2. **Access API Documentation:**
API documentation is available at the `/docs` endpoint for each service

3. **Test Database Connectivity:**
The health check endpoints will verify database connections.

## Testing

### Running Tests

#### All Tests
```bash
pytest
```

#### Service-Specific Tests
```bash
# Discord service tests
pytest tests/discord/

# Trading service tests  
pytest tests/trading/
```

#### Test Categories
```bash
# Unit tests only
pytest -m unit

# Slow tests (integration)
pytest -m slow
```

#### Coverage Report
```bash
pytest --cov=app --cov-report=html
```

### Test Requirements
Install test dependencies:
```bash
pip install -r app/discord/requirements-test.txt
pip install -r app/trading/requirements-test.txt
```

## Project Architecture

### Service Structure
```
algobot-signal-trading/
├── app/
│   ├── discord/          # Discord message processing service
│   │   ├── main.py       # FastAPI application entry
│   │   ├── config.py     # Configuration management
│   │   ├── models/       # Data models
│   │   ├── services/     # Business logic
│   │   └── routers/      # API endpoints
│   └── trading/          # Trading automation service
│       ├── main.py       # FastAPI application entry
│       ├── config.py     # Configuration management
│       ├── models/       # Trading models
│       │   └── okx/      # OKX exchange models
│       ├── services/     # Trading services
│       └── routers/      # Trading API endpoints
├── shared/               # Shared utilities and middleware
├── domain/               # Domain entities and common logic
├── tests/                # Test suites
└── docker-compose.dev.yml # Development environment
```

### Technology Stack
- **Framework**: FastAPI (Python 3.12)
- **Database**: MongoDB with Motor (async driver)
- **Cache**: Redis
- **Trading Platform**: OKX Exchange
- **Containerization**: Docker & Docker Compose
- **Testing**: pytest with coverage

### API Architecture
- RESTful API design
- Async/await throughout
- Pydantic models for validation
- Structured logging
- Health checks and monitoring

### Development Workflow
1. Make code changes
2. Run tests: `pytest`
3. Start services: `docker-compose up`
4. Test endpoints via docs or curl
5. Check logs for issues
6. Commit and push changes

## Getting Help

### Documentation
- **API Docs**: Available at `/docs` endpoint for each service
- **OpenAPI Spec**: Available at `/openapi.json`

### Support
- Check logs first: `docker-compose logs -f`
- Verify environment configuration
- Test database connectivity
- Review this setup guide

---

**Happy Trading! 🚀**

> **Security Note**: Never commit your `.env` file or expose production credentials. Keep your API keys and tokens secure.