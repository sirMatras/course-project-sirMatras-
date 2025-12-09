# P10 — SAST & Secrets

Артефакты формируются в CI workflow `Security - SAST & Secrets`:

- `EVIDENCE/P10/semgrep.sarif` — отчёт Semgrep (профиль `p/ci` + `security/semgrep/rules.yml`).
- `EVIDENCE/P10/gitleaks.json` — отчёт Gitleaks по рабочей копии репозитория.

Локальный запуск (опционально, аналог CI):

```bash
docker run --rm -v "$PWD:/src" returntocorp/semgrep:1.83.0 \
  semgrep ci --config p/ci --config /src/security/semgrep/rules.yml \
    --sarif --output /src/EVIDENCE/P10/semgrep.sarif --metrics=off || true

docker run --rm -v "$PWD:/repo" zricethezav/gitleaks:8.18.4 \
  detect --no-banner --config=/repo/security/.gitleaks.toml \
    --source=/repo --report-format=json \
    --report-path=/repo/EVIDENCE/P10/gitleaks.json || true
```

По итогам прогона в PR фиксируется краткое резюме: наличие findings, план действий и ссылки на артефакты job.

