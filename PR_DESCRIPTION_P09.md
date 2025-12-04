## P09 — SBOM, SCA и артефакты

Этот PR добавляет поддержку практики **P09**: генерация SBOM, SCA‑отчётов и хранение артефактов.

### C1. SBOM — покрытие и автоматизация

- Добавлен отдельный workflow `.github/workflows/sbom-sca.yml`.
- При каждом `push`/`pull_request` по релевантным путям и при `workflow_dispatch`:
  - генерируется **SBOM** с помощью Syft (`anchore/syft:v0.104.0`) из содержимого репозитория;
  - результат сохраняется в `EVIDENCE/P09/sbom.json`.
- Используется фиксированная версия образа Syft для воспроизводимости.

### C2. SCA — отчёт и сводка по уязвимостям

- По сгенерированному SBOM запускается **SCA** с помощью Grype (`anchore/grype:v0.80.0`).
- Полный отчёт сохраняется в `EVIDENCE/P09/sca_report.json`.
- На основе `sca_report.json` формируется `EVIDENCE/P09/sca_summary.md`:
  - агрегированные счётчики уязвимостей по severity (CRITICAL/HIGH/MEDIUM/LOW/…),
  - ссылка на конкретный workflow run и commit.
- При повторном прогоне на том же коммите отчёты воспроизводимы (фиксированные версии Syft/Grype).

### C3. Артефакты и трассировка (Evidence & DS1)

- Все ключевые артефакты складываются в `EVIDENCE/P09/`:
  - `sbom.json`,
  - `sca_report.json`,
  - `sca_summary.md`.
- Workflow публикует их как артефакт GitHub Actions `sbom-sca-artifacts`.
- В `EVIDENCE/P09/README.md` описана структура каталога и как использовать эти файлы
  для **DS‑раздела** итогового отчёта (трассировка от commit/job к анализу уязвимостей).

### C4. Политика и waivers

- Добавлен файл политики `policy/waivers.yml`:
  - описана общая политика работы с уязвимостями (Critical/High/Medium/Low),
  - задана структура waivers (id, package, severity, reason, owner, issue, review_until, notes),
  - есть пример **осознанного waiver** с обоснованием, ссылкой на Issue и сроком пересмотра.
- В дальнейшем планируется:
  - оформлять реальные waivers для допустимых уязвимостей;
  - по возможности заменять waivers на реальные фиксы (обновление зависимостей/кода).

### C5. Интеграция в CI и гигиена

- Workflow `SBOM & SCA`:
  - триггерится на `push`/`pull_request` по релевантным путям (`src/**`, `requirements*.txt`, `Dockerfile`, `policy/waivers.yml`),
  - имеет `workflow_dispatch` для ручного запуска,
  - использует разумный `timeout-minutes` и **не трогает секреты** (только публичные образы Syft/Grype),
  - загружает артефакты с помощью `actions/upload-artifact@v4`.
- Задан `concurrency` для группы `sbom-sca-${{ github.ref }}`, чтобы старые запуски не зависали.
- Workflow логически дополняет существующий `ci.yml` из P08 и не конфликтует с ним.


