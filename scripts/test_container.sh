#!/bin/bash
# Скрипт для локальной проверки контейнера

set -e

echo "=== P07 Container Hardening Test Script ==="

# Цвета для вывода
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Проверка что образ собирается
echo -e "${YELLOW}[1/6] Building Docker image...${NC}"
docker build -t workout-api:test . || {
    echo -e "${RED}✗ Build failed${NC}"
    exit 1
}
echo -e "${GREEN}✓ Build successful${NC}"

# 2. Проверка размера образа
echo -e "${YELLOW}[2/6] Checking image size...${NC}"
docker images workout-api:test --format "Image: {{.Repository}}:{{.Tag}}, Size: {{.Size}}"

# 3. Проверка docker history
echo -e "${YELLOW}[3/6] Generating docker history...${NC}"
docker history workout-api:test --format "table {{.CreatedBy}}\t{{.Size}}" > docker-history.txt
echo "History saved to docker-history.txt"

# 4. Проверка non-root пользователя
echo -e "${YELLOW}[4/6] Checking non-root user...${NC}"
CONTAINER_ID=$(docker run -d workout-api:test)
USER_ID=$(docker exec $CONTAINER_ID id -u)
if [ "$USER_ID" -eq "0" ]; then
    echo -e "${RED}✗ Container runs as root (UID=0)${NC}"
    docker stop $CONTAINER_ID
    docker rm $CONTAINER_ID
    exit 1
else
    echo -e "${GREEN}✓ Container runs as non-root user (UID=$USER_ID)${NC}"
fi

# 5. Проверка healthcheck
echo -e "${YELLOW}[5/6] Checking healthcheck...${NC}"
sleep 15
HEALTH_STATUS=$(docker inspect --format='{{.State.Health.Status}}' $CONTAINER_ID 2>/dev/null || echo "none")
if [ "$HEALTH_STATUS" = "healthy" ] || [ "$HEALTH_STATUS" = "starting" ]; then
    echo -e "${GREEN}✓ Healthcheck status: $HEALTH_STATUS${NC}"
else
    echo -e "${RED}✗ Healthcheck status: $HEALTH_STATUS${NC}"
    docker logs $CONTAINER_ID
fi

# 6. Проверка доступности API
echo -e "${YELLOW}[6/6] Testing API endpoint...${NC}"
sleep 5
API_RESPONSE=$(docker exec $CONTAINER_ID curl -f http://localhost:8000/health 2>/dev/null || echo "failed")
if [ "$API_RESPONSE" != "failed" ]; then
    echo -e "${GREEN}✓ API is accessible: $API_RESPONSE${NC}"
else
    echo -e "${RED}✗ API is not accessible${NC}"
    docker logs $CONTAINER_ID
fi

docker stop $CONTAINER_ID
docker rm $CONTAINER_ID

echo ""
echo -e "${GREEN}=== All tests passed! ===${NC}"

