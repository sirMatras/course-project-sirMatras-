# P11 — DAST (OWASP ZAP Baseline)

Артефакты формируются в CI workflow `Security - DAST (ZAP Baseline)`:

- `EVIDENCE/P11/zap_baseline.html` — человекочитаемый HTML-отчёт ZAP baseline scan.
- `EVIDENCE/P11/zap_baseline.json` — JSON-отчёт ZAP для программной обработки.

## Что сканируется

**Target URL:** `http://localhost:8000/` (FastAPI приложение)

**Endpoints:**
- `GET /health` — health check endpoint
- `POST /items?name=...` — создание элемента
- `GET /items/{id}` — получение элемента

## Локальный запуск (опционально)

### 1. Поднять приложение

```bash
# Вариант 1: Docker
docker build -t secdev-app .
docker run -d --name secdev-app -p 8000:8000 secdev-app

# Вариант 2: Docker Compose
docker compose up -d

# Вариант 3: Прямой запуск
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 2. Дождаться готовности

```bash
curl http://localhost:8000/health
# Должен вернуть: {"status": "ok"}
```

### 3. Запустить ZAP baseline

```bash
mkdir -p EVIDENCE/P11

docker run --rm \
  -v "${PWD}/EVIDENCE/P11:/zap/wrk/:rw" \
  -t owasp/zap2docker-stable:latest \
  zap-baseline.py \
  -t http://host.docker.internal:8000 \
  -J zap_baseline.json \
  -r zap_baseline.html \
  -g gen.conf \
  -I \
  -j
```

**Параметры ZAP:**
- `-t` — target URL для сканирования
- `-J` — JSON отчёт
- `-r` — HTML отчёт
- `-g` — генерация конфига
- `-I` — не завершать при ошибках
- `-j` — JSON формат вывода

## Интерпретация результатов

### Уровни алертов

- **High** — критические уязвимости, требуют немедленного исправления
- **Medium** — важные проблемы безопасности, рекомендуется исправить
- **Low** — информационные предупреждения, могут быть ложными срабатываниями
- **Informational** — информационные сообщения, обычно не критичны

### Типичные findings для FastAPI

- **Missing Anti-Clickjacking Header** — отсутствие X-Frame-Options
- **Missing Content-Type Header** — отсутствие Content-Type в некоторых ответах
- **X-Content-Type-Options Header Missing** — отсутствие защиты от MIME sniffing
- **Server Leaks Information via "X-Powered-By"** — утечка информации о сервере

### План действий

1. Просмотреть HTML-отчёт для визуального анализа
2. Выделить реально значимые проблемы (High/Medium)
3. Исправить критичные уязвимости или обосновать принятие риска
4. Обновить описание PR с результатами триажа

## Использование результатов в DS-разделе

Результаты DAST-сканирования используются для:
- Валидации threat model (подтверждение/опровержение предположений)
- Демонстрации эффективности security controls
- Планирования улучшений безопасности
- Трассируемости от кода к реальным уязвимостям

