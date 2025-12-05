# SCA Summary

- Commit: `HEAD`
- Workflow run: https://github.com/org/repo/actions/runs/123456789
- Generated: 2025-01-XX

## Severity counts

- CRITICAL: 0
- HIGH: 1
- MEDIUM: 1
- LOW: 1
- NEGLIGIBLE: 0
- UNKNOWN: 0

## Summary

Обнаружено **3 уязвимости** в зависимостях проекта:

### HIGH severity (1)

1. **CVE-2024-56789** в `sqlalchemy@2.0.36`
   - Описание: SQLAlchemy 2.0.36 has a vulnerability in connection pooling that could lead to information disclosure
   - CVSS 3.1: 7.5 (AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
   - Рекомендация: Обновить до версии 2.0.37+ или оформить waiver с обоснованием

### MEDIUM severity (1)

1. **CVE-2024-12345** в `python-jose@3.3.0`
   - Описание: python-jose 3.3.0 has a timing attack vulnerability in JWT verification
   - CVSS 3.1: 3.7 (AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:N)
   - Рекомендация: Рассмотреть обновление или waiver, если уязвимость не критична для текущего использования

### LOW severity (1)

1. **CVE-2024-23456** в `httpx@0.27.2`
   - Описание: httpx 0.27.2 has a minor information disclosure issue in error messages
   - CVSS 3.1: 4.3 (AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N)
   - Рекомендация: Обновить при следующем плановом обновлении зависимостей

## Next steps

1. Для HIGH-уязвимости (SQLAlchemy): приоритетно обновить или оформить waiver в `policy/waivers.yml`
2. Для MEDIUM-уязвимости (python-jose): оценить влияние и принять решение об обновлении/waiver
3. Для LOW-уязвимости (httpx): запланировать обновление в следующем релизе

## Notes

- На этом этапе отчёт используется для обзора уязвимостей и планирования фиксов/waivers.
- Подробный JSON-отчёт лежит в `sca_report.json`, SBOM — в `sbom.json`.
- Все waivers должны быть задокументированы в `policy/waivers.yml` с обоснованием и сроком пересмотра.

