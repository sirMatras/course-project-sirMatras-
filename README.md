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

## Безопасность и артефакты (P07–P09)

- **P07 — Container security**: см. `PR_DESCRIPTION_P07.md` и workflow `ci.yml` (job `container-security`).
- **P08 — CI/CD**: см. `PR_DESCRIPTION_P08.md` и общий workflow `ci.yml`.
- **P09 — SBOM & SCA**:
  - отдельный workflow `.github/workflows/sbom-sca.yml`;
  - артефакты складываются в `EVIDENCE/P09/`:
    - `sbom.json` — SBOM (Syft),
    - `sca_report.json` — отчёт SCA (Grype),
    - `sca_summary.md` — человекочитаемая сводка;
  - политика работы с уязвимостями и waivers описана в `policy/waivers.yml`.

## Контейнеры
```bash
docker build -t secdev-app .
docker run --rm -p 8000:8000 secdev-app
# или
docker compose up --build
```

## Эндпойнты
- `GET /health` → `{"status": "ok"}`
- `POST /items?name=...` — демо-сущность
- `GET /items/{id}`

## Формат ошибок
Все ошибки — JSON-обёртка:
```json
{
  "error": {"code": "not_found", "message": "item not found"}
}
```

См. также: `SECURITY.md`, `.pre-commit-config.yaml`, `.github/workflows/ci.yml`.

test
"## P02: Workflow demonstration"
