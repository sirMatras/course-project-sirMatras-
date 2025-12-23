# P10 — SAST & Secrets

Артефакты формируются в CI workflow `Security - SAST & Secrets`:

- `EVIDENCE/P10/semgrep.sarif` — отчёт Semgrep в формате SARIF (профиль `p/ci` + кастомные правила `security/semgrep/rules.yml`).
- `EVIDENCE/P10/gitleaks.json` — отчёт Gitleaks в формате JSON по рабочей копии репозитория.
- `EVIDENCE/P10/sast_summary.md` — краткий summary с триажем findings и планом действий.

## Локальный запуск (опционально, аналог CI)

### Semgrep

```bash
mkdir -p EVIDENCE/P10

docker run --rm -v "$PWD:/src" returntocorp/semgrep:latest \
  semgrep ci \
    --config p/ci \
    --config /src/security/semgrep/rules.yml \
    --sarif --output /src/EVIDENCE/P10/semgrep.sarif \
    --metrics=off || true
```

### Gitleaks

```bash
docker run --rm -v "$PWD:/repo" zricethezav/gitleaks:latest \
  detect --no-banner \
    --config=/repo/security/.gitleaks.toml \
    --source=/repo \
    --report-format=json \
    --report-path=/repo/EVIDENCE/P10/gitleaks.json || true
```

## Использование результатов

1. **Просмотр отчётов:** откройте `semgrep.sarif` и `gitleaks.json` для детального анализа.
2. **Summary:** см. `sast_summary.md` для краткого обзора findings и плана действий.
3. **GitHub Actions:** артефакты доступны в workflow run как `sast-secrets-artifacts`.
4. **GitHub Security:** SARIF отчёты автоматически загружаются в Code Scanning.

По итогам прогона в PR фиксируется краткое резюме: наличие findings, план действий и ссылки на артефакты job.

