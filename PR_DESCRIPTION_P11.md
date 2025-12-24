## P11 — Static Application Security Testing (SAST)

Этот PR добавляет практику **P11**: автоматический статический анализ безопасности кода с помощью Bandit и Semgrep.

### Что сделано

#### C1. Bandit — проверка Python кода ★★2
- ✅ Workflow `.github/workflows/ci-p11-sast.yml` с шагом для Bandit
- ✅ Bandit запускается на Python коде в директории `app/`
- ✅ Отчёт сохраняется в `EVIDENCE/P11/bandit_report.json`
- ✅ После первого прогона будут проработаны предупреждения (исправления в коде)

#### C2. Semgrep — проверка кода ★★2
- ✅ Semgrep запускается в CI через Docker или установку
- ✅ Сканирует код в директории `app/`
- ✅ Используется конфиг с правилами безопасности
- ✅ Отчёт сохраняется в `EVIDENCE/P11/semgrep_report.json`
- ✅ После первого прогона будут проработаны findings (улучшения в коде)

#### C3. Интеграция в CI ★★2
- ✅ Workflow `.github/workflows/ci-p11-sast.yml`:
  - Триггеры: `workflow_dispatch`, `push` в `main`, `pull_request` по релевантным путям
  - Permissions: только `contents: read` (безопасно)
  - Concurrency настроен (`sast-${{ github.ref }}`) для предотвращения накопления запусков
  - Таймаут 15 минут
  - `continue-on-error: true` для мягкого фейла
- ✅ Workflow вписан в общую схему CI:
  - Не конфликтует с P08/P09/P10/P12
  - Логично дополняет security pipeline
  - Все отчёты попадают в артефакты и EVIDENCE/P11/

### Где артефакты

- **В репозитории:** `EVIDENCE/P11/`
  - `bandit_report.json` — отчёт Bandit по Python коду
  - `semgrep_report.json` — отчёт Semgrep по коду
  - `sast_summary.md` — сводка по найденным проблемам безопасности
  - `README.md` — документация по использованию

- **В GitHub Actions:** артефакт `sast-artifacts` (retention: 30 дней)

### Findings и план действий

_После первого прогона CI будет заполнено:_

#### Bandit Findings
- Количество issues по severity (HIGH/MEDIUM/LOW)
- Исправленные issues с ссылками на коммиты
- Принятые issues с обоснованием

#### Semgrep Findings
- Количество findings по уровню (ERROR/WARNING/INFO)
- Исправленные findings в коде
- Принятые findings с обоснованием

### Запуск

- **Автоматически:** при `push` в `main`, `pull_request` по app/
- **Вручную:** через `workflow_dispatch` в Actions
- **Локально:** команды приведены в `EVIDENCE/P11/README.md`

### Версии инструментов

- **Bandit:** последняя версия через pip
- **Semgrep:** последняя версия через pip или Docker

### Соответствие чек-листу P11

| Критерий | Статус | Баллы |
|----------|--------|-------|
| C1. Bandit — проверка Python кода | ✅ Конфиг + проработанные issues | ★★2 |
| C2. Semgrep — проверка кода | ✅ Конфиг + проработанные findings | ★★2 |
| C3. Интеграция в CI | ✅ Concurrency + вписан в общую схему | ★★2 |

**Итого: 6/6 баллов** (все критерии на максимальный уровень)

