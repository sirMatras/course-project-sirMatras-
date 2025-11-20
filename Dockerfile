# P07: Container hardening - Multi-stage build для минимального образа
# Build stage: установка зависимостей и тестирование
FROM python:3.11-slim AS build

# Установка переменных окружения для сборки
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

# Кэш-слои: копируем зависимости отдельно для лучшего кэширования
COPY requirements.txt requirements-dev.txt ./

# Установка зависимостей для разработки (включая pytest для тестов)
# Слой кэшируется отдельно от кода, что ускоряет пересборки
RUN pip install --no-cache-dir --upgrade pip==24.2 && \
    pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt

# Копируем исходный код и тесты только после установки зависимостей
# Это позволяет переиспользовать кэш слоя с зависимостями
COPY src/ ./src/
COPY tests/ ./tests/
COPY pyproject.toml ./

# Запуск тестов на этапе сборки
RUN pytest -q || exit 1

# Runtime stage: минимальный финальный образ
FROM python:3.11-slim

# Установка curl для healthcheck (минимальный размер)
# Объединено в один слой для уменьшения размера образа
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl ca-certificates && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Создание непривилегированного пользователя
RUN groupadd -r appuser && \
    useradd -r -g appuser -u 1000 -m -d /app -s /bin/bash appuser

WORKDIR /app

# Копируем только production зависимости из build stage
COPY --from=build /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=build /usr/local/bin /usr/local/bin

# Копируем только необходимые файлы приложения
COPY --chown=appuser:appuser src/ ./src/

# Устанавливаем переменные окружения
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/src \
    PATH=/usr/local/bin:$PATH

# Создаём директорию для данных с правильными правами
RUN mkdir -p /app/data && \
    chown -R appuser:appuser /app

# Меняем пользователя на непривилегированного
USER appuser

# Ограничиваем capabilities (DROP ALL, только необходимые)
# Это делается через docker-compose, но можно указать здесь через docker run

# Открываем порт
EXPOSE 8000

# HEALTHCHECK с таймаутами
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Явное объявление ENTRYPOINT и CMD
ENTRYPOINT ["python", "-m", "uvicorn"]
CMD ["app.main:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "src"]
