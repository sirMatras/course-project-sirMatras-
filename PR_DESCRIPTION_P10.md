## P10 — SAST & Secrets

Этот PR добавляет практику **P10**: Semgrep (SAST) и Gitleaks (secrets) с артефактами.

### Что сделано
- Новый workflow `.github/workflows/ci-sast-secrets.yml` с job **Security - SAST & Secrets** (Semgrep p/ci + `security/semgrep/rules.yml`, Gitleaks с `security/.gitleaks.toml`).
- Артефакты складываются в `EVIDENCE/P10/`: `semgrep.sarif`, `gitleaks.json` (публикуются как artifact `sast-secrets-artifacts`).
- Добавлены кастомные правила Semgrep для детекта хардкода секретов и `verify=False`.
- Gitleaks конфигурирован с allowlist для известных безопасных строк из документации.

### Где артефакты
- `EVIDENCE/P10/semgrep.sarif`
- `EVIDENCE/P10/gitleaks.json`
- Workflow: `Security - SAST & Secrets` (Actions)

### Findings и план (обновить после прогона CI)
- Semgrep: _TBD после последнего запуска (указать count по severity и действия)_.
- Gitleaks: _TBD (указать, есть ли реальные секреты; ложноположительные занесены в allowlist)_.

### Запуск
- Авто: `push` в `main`, `pull_request` по коду и security-конфигам, `workflow_dispatch`.
- Локально (опционально): команды приведены в `EVIDENCE/P10/README.md`.

