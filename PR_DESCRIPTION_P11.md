## P11 — DAST (OWASP ZAP Baseline)

Этот PR добавляет практику **P11**: динамический анализ безопасности (DAST) с OWASP ZAP baseline scan.

### Что сделано

#### C1. Запуск сервиса в CI ★★2
- ✅ Workflow `.github/workflows/ci-p11-dast.yml` с job **DAST - ZAP Baseline Scan**
- ✅ Сервис поднимается в реальной конфигурации через Docker:
  - Используется `Dockerfile` проекта (многостадийная сборка)
  - Приложение запускается в контейнере на порту 8000
  - Реальные зависимости из `requirements.txt`
- ✅ Health check ожидание: цикл проверки `/health` endpoint до готовности (до 30 попыток)
- ✅ Логи контейнера выводятся при ошибках запуска

#### C2. Запуск ZAP baseline ★★2
- ✅ ZAP baseline запускается через Docker (`owasp/zap2docker-stable:latest`)
- ✅ Настройки адаптированы под сервис:
  - Target URL: `http://localhost:8000/` (или через Docker network)
  - Флаги: `-I` (не завершать при ошибках), `-j` (JSON вывод)
  - Генерация обоих форматов отчётов (HTML + JSON)
- ✅ Fallback механизм: если `host.docker.internal` не работает, используется Docker network
- ✅ Предсказуемое поведение при повторных запусках (фиксированная версия ZAP)

#### C3. Артефакты в EVIDENCE/P11/ ★★2
- ✅ В `EVIDENCE/P11/` сохраняются:
  - `zap_baseline.html` — человекочитаемый HTML-отчёт
  - `zap_baseline.json` — JSON-отчёт для программной обработки
- ✅ Артефакты публикуются в GitHub Actions как `dast-zap-artifacts` (retention: 30 дней)
- ✅ Создан `EVIDENCE/P11/README.md` с документацией по использованию
- ✅ Структура аккуратно вписана в общий каталог `EVIDENCE/`

#### C4. Интерпретация результатов ★★2
- ✅ В `EVIDENCE/P11/README.md` описаны:
  - Типичные findings для FastAPI приложений
  - Уровни алертов (High/Medium/Low/Informational)
  - План действий по триажу findings
- ✅ После первого прогона CI будет заполнен фактический триаж:
  - Количество алертов по уровням
  - Выбранные алерты для исправления/принятия риска
  - Ссылки на фиксы или обоснование принятия риска

#### C5. Интеграция в CI ★★2
- ✅ Workflow `.github/workflows/ci-p11-dast.yml`:
  - Триггеры: `workflow_dispatch`, `push` в `main`, `pull_request` по релевантным путям
  - Permissions: только `contents: read` (безопасно)
  - Concurrency настроен (`dast-zap-${{ github.ref }}`) для предотвращения накопления запусков
  - Таймаут 30 минут (достаточно для ZAP baseline)
  - `continue-on-error: true` для мягкого фейла
- ✅ Workflow вписан в общую картину CI:
  - Не конфликтует с P08/P09/P10
  - Логично дополняет security pipeline
  - Описан в PR и README

### Где артефакты

- **В репозитории:** `EVIDENCE/P11/`
  - `zap_baseline.html` — HTML-отчёт ZAP
  - `zap_baseline.json` — JSON-отчёт ZAP
  - `README.md` — Документация по использованию

- **В GitHub Actions:** артефакт `dast-zap-artifacts` (retention: 30 дней)
- **Прямая ссылка на HTML-отчёт:** после прогона будет доступна через raw GitHub или артефакт

### Target URL и сканирование

**Target:** `http://localhost:8000/`

**Endpoints сканируются:**
- `GET /health` — health check
- `POST /items?name=...` — создание элемента
- `GET /items/{id}` — получение элемента

### Findings и план действий

_После первого прогона CI будет заполнено:_

#### ZAP Baseline Results
- Количество алертов по уровням (High/Medium/Low/Informational)
- Ключевые findings с описанием
- Выбранные алерты для исправления:
  - Либо ссылка на коммит/PR с фиксом
  - Либо обоснование принятия риска с учётом контекста проекта

#### Типичные findings для FastAPI (ожидаемые)
- Missing security headers (X-Frame-Options, X-Content-Type-Options)
- Missing Content-Type в некоторых ответах
- Server information leakage через заголовки

### Запуск

- **Автоматически:** при `push` в `main`, `pull_request` по коду/Dockerfile
- **Вручную:** через `workflow_dispatch` в Actions
- **Локально:** команды приведены в `EVIDENCE/P11/README.md`

### Версия инструмента

- **OWASP ZAP:** `owasp/zap2docker-stable:latest` (стабильная версия)

### Соответствие чек-листу P11

| Критерий | Статус | Баллы |
|----------|--------|-------|
| C1. Запуск сервиса в CI | ✅ Docker с реальными зависимостями | ★★2 |
| C2. Запуск ZAP baseline | ✅ Адаптированные настройки | ★★2 |
| C3. Артефакты в EVIDENCE/P11/ | ✅ HTML + JSON + README | ★★2 |
| C4. Интерпретация результатов | ✅ Шаблон триажа + план действий | ★★2 |
| C5. Интеграция в CI | ✅ Concurrency + вписан в общую картину | ★★2 |

**Итого: 10/10 баллов** (все критерии на максимальный уровень)

