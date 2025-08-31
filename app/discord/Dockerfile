# Base stage - common dependencies
FROM python:3.12-slim as base

WORKDIR /app

# Copy requirements first for better caching
COPY app/discord/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Expose ports
EXPOSE 3000
EXPOSE 3999

# Development stage
FROM base as development
# Don't copy code - it will be mounted via volumes
CMD ["uvicorn", "app.discord.main:app", "--host", "0.0.0.0", "--port", "3000", "--reload"]

# Production stage
FROM base as production
# Copy application code for production
COPY app/ ./app/
COPY shared/ ./shared/
COPY domain/ ./domain/
COPY .env .
CMD ["uvicorn", "app.discord.main:app", "--host", "0.0.0.0", "--port", "3000"]