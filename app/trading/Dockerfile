# Base stage - common dependencies
FROM python:3.12-slim as base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY app/trading/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Expose ports
EXPOSE 3010
EXPOSE 3019

# Development stage
FROM base as development
# Don't copy code - it will be mounted via volumes
CMD ["uvicorn", "app.trading.main:app", "--host", "0.0.0.0", "--port", "3010", "--reload"]

# Production stage
FROM base as production
# Copy application code for production
COPY app/ ./app/
COPY shared/ ./shared/
COPY domain/ ./domain/
COPY .env .
CMD ["uvicorn", "app.trading.main:app", "--host", "0.0.0.0", "--port", "3010"]