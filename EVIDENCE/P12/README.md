# P12 — IaC & Container Security

Артефакты формируются в CI workflow `Security - IaC & Container (Hadolint, Checkov, Trivy)`:

- `EVIDENCE/P12/hadolint_report.json` — отчёт Hadolint по Dockerfile.
- `EVIDENCE/P12/checkov_report.json` — отчёт Checkov по IaC (Dockerfile, Docker Compose).
- `EVIDENCE/P12/trivy_report.json` — отчёт Trivy по контейнерному образу.
- `EVIDENCE/P12/hardening_summary.md` — сводка по мерам харднинга.

## Инструменты

### Hadolint
- **Назначение:** Линтинг Dockerfile на best practices и security issues
- **Конфиг:** `security/hadolint.yaml`
- **Отчёт:** JSON формат для программной обработки

### Checkov
- **Назначение:** Сканирование Infrastructure as Code (Dockerfile, Docker Compose, K8s, Terraform)
- **Конфиг:** `security/checkov.yaml`
- **Отчёт:** JSON формат с findings по security checks

### Trivy
- **Назначение:** Сканирование контейнерных образов на уязвимости
- **Конфиг:** `security/trivy.yaml`
- **Отчёт:** JSON формат с детальной информацией об уязвимостях

## Локальный запуск (опционально)

### Hadolint

```bash
mkdir -p EVIDENCE/P12

docker run --rm \
  -v "${PWD}:/mnt" \
  -w /mnt \
  hadolint/hadolint:latest \
  hadolint \
  --config security/hadolint.yaml \
  --format json \
  Dockerfile > EVIDENCE/P12/hadolint_report.json
```

### Checkov

```bash
docker run --rm \
  -v "${PWD}:/mnt" \
  -w /mnt \
  bridgecrew/checkov:latest \
  --directory /mnt \
  --framework dockerfile docker_compose \
  --config-file security/checkov.yaml \
  --output json \
  --output-file-path EVIDENCE/P12/checkov_report.json
```

### Trivy

```bash
# Сначала соберите образ
docker build -t secdev-app:test .

# Затем сканируйте
docker run --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v "${PWD}/EVIDENCE/P12:/output" \
  aquasec/trivy:latest \
  image \
  --config security/trivy.yaml \
  --format json \
  --output /output/trivy_report.json \
  secdev-app:test
```

## Интерпретация результатов

### Hadolint
- **ERROR:** Критические проблемы безопасности, требуют исправления
- **WARNING:** Важные best practices, рекомендуется исправить
- **INFO:** Информационные сообщения

### Checkov
- **PASSED:** Проверка пройдена
- **FAILED:** Найдена проблема безопасности
- **SKIPPED:** Проверка пропущена (по конфигу)

### Trivy
- **CRITICAL:** Критические уязвимости, требуют немедленного исправления
- **HIGH:** Высокие уязвимости, рекомендуется исправить
- **MEDIUM:** Средние уязвимости, рассмотреть исправление
- **LOW:** Низкие уязвимости, обычно не критичны

## Меры харднинга

Подробное описание применённых мер харднинга см. в `hardening_summary.md`.

### Dockerfile
- Non-root user с конкретным UID/GID
- Правильное владение файлами
- Security environment variables
- Улучшенный healthcheck
- Очистка build dependencies

### Docker Compose
- Ограничение сетевого доступа (localhost only)
- Security options (no-new-privileges)
- Restart policy
- Healthcheck configuration

## Использование результатов в DS-разделе

Результаты P12 используются для:
- Демонстрации мер харднинга контейнеров и IaC
- Валидации security controls
- Планирования улучшений безопасности инфраструктуры
- Трассируемости от конфигурации к реальным улучшениям

