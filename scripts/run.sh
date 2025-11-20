#!/bin/bash
# Скрипт для локального запуска приложения через docker-compose

set -e

echo "=== Starting Workout API with docker-compose ==="

# Проверка наличия .env файла
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example (if exists)..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "⚠️  Please update .env with your secrets!"
    else
        echo "⚠️  .env file not found. Creating basic one..."
        cat > .env << EOF
# Database
POSTGRES_DB=workout_db
POSTGRES_USER=workout_user
POSTGRES_PASSWORD=$(openssl rand -hex 16)

# API
API_PORT=8000
JWT_SECRET=$(openssl rand -hex 32)
JWT_ALGORITHM=HS256

# App
APP_ENV=development
DATABASE_URL=postgresql://workout_user:\${POSTGRES_PASSWORD}@postgres:5432/workout_db
CORS_ALLOW_ORIGINS=*
EOF
        echo "⚠️  Basic .env created. Please review and update secrets!"
    fi
fi

# Запуск через docker-compose
echo "Building and starting services..."
docker compose up -d --build

echo ""
echo "Waiting for services to be healthy..."
sleep 10

# Проверка статуса
docker compose ps

echo ""
echo "=== Services started ==="
echo "API: http://localhost:${API_PORT:-8000}"
echo "API Docs: http://localhost:${API_PORT:-8000}/docs"
echo ""
echo "To view logs: docker compose logs -f"
echo "To stop: docker compose down"

