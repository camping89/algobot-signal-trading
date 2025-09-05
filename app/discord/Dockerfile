# Base stage - common dependencies
FROM python:3.12-slim as base

WORKDIR /app

# Copy requirements first for better caching
COPY app/discord/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Expose ports
EXPOSE 3000
EXPOSE 3009

# Development stage
FROM base as development
# Don't copy code - it will be mounted via volumes
CMD ["uvicorn", "app.discord.main:app", "--host", "0.0.0.0", "--port", "3000", "--reload"]

# Debug stage for PyCharm
FROM base as debug
# Don't copy code - it will be mounted via volumes
# Install PyCharm debugger
RUN pip install pydevd-pycharm==252.25557.178
EXPOSE 5678
# Set environment variables for PyCharm debug
ENV PYTHONPATH=/app
ENV PYCHARM_DEBUG=true
ENV PYCHARM_DEBUG_PORT=5678
ENV PYCHARM_DEBUG_HOST=host.docker.internal
CMD ["python", "-Xfrozen_modules=off", "-m", "uvicorn", "app.discord.main:app", "--host", "0.0.0.0", "--port", "3000", "--reload"]

# Production stage
FROM base as production
# Copy application code for production
COPY app/ ./app/
COPY shared/ ./shared/
COPY domain/ ./domain/
COPY .env .
CMD ["uvicorn", "app.discord.main:app", "--host", "0.0.0.0", "--port", "3000"]