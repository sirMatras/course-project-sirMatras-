# SecDev Course Template

Стартовый шаблон для студенческого репозитория (HSE SecDev 2025).

## Быстрый старт
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt -r requirements-dev.txt
pre-commit install
uvicorn app.main:app --reload
```

## Ритуал перед PR
```bash
ruff check --fix .
black .
isort .
pytest -q
pre-commit run --all-files
```

## Тесты
```bash
pytest -q
```

## CI
В репозитории настроен workflow **CI** (GitHub Actions) — required check для `main`.
Badge добавится автоматически после загрузки шаблона в GitHub.

## Контейнеры
```bash
docker build -t secdev-app .
docker run --rm -p 8000:8000 secdev-app
# или
docker compose up --build
```

## Эндпойнты
- `GET /health` → `{"status": "ok"}`
- `POST /auth/register` — регистрация, тело: `{email, password}`
- `POST /auth/login` — логин, ответ: `{access_token, refresh_token, token_type}`
- `POST /auth/refresh` — обновление пары токенов
- `POST /auth/logout` — статeless логаут
- CRUD: `/api/v1/exercises`, `/api/v1/workouts`, `/api/v1/stats`

## Формат ошибок (RFC 7807)
Все ошибки возвращаются в формате `application/problem+json` с полями:
```json
{
  "type": "https://example.com/problems/not-found",
  "title": "Not Found",
  "status": 404,
  "detail": "...",
  "correlation_id": "..."
}
```

### Rate limiting
Для `/auth/login` действует лимит: 5 запросов за 60 секунд на IP. При превышении — `429 Too Many Requests` в RFC7807 формате.

### ADR
- `docs/adr/ADR-001-errors-rfc7807.md`
- `docs/adr/ADR-002-rate-limiting-login.md`
- `docs/adr/ADR-003-secrets-management.md`

См. также: `SECURITY.md`, `.pre-commit-config.yaml`, `.github/workflows/ci.yml`.

test
"## P02: Workflow demonstration"
