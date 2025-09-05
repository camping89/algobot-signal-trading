#!/bin/bash

# make this file executable with: chmod +x script/<filename>

COMPOSE_FILE="docker-compose.debug.yml"
SERVICES="discord-debug trading-debug"

# Stop running containers
docker-compose -f "$COMPOSE_FILE" stop $SERVICES

# Remove stopped containers (forcefully)
docker-compose -f "$COMPOSE_FILE" rm -f $SERVICES

# Recreate and start in detached mode
docker-compose -f "$COMPOSE_FILE" up -d $SERVICES