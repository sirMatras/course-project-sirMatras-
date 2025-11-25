# P08: CI/CD Pipeline

## Краткое описание

Данный PR реализует полноценный CI/CD pipeline согласно требованиям P08 для оценки 10 (★★2 по всем критериям):

### Реализованные улучшения:

1. **C1 (★★2): Матрица сборки и тестов**
   - Матрица: Python 3.11, 3.12 на Ubuntu и Windows
   - Параллельные шаги для ускорения CI
   - Кэш зависимостей для всех версий Python

2. **C2 (★★2): Оптимизированное кэширование**
   - Кэш pip по хешу `requirements.txt` и `requirements-dev.txt`
   - Кэш по `pyproject.toml` для Python пакетов
   - Docker layer cache через GitHub Actions cache (type=gha)
   - Ключи кэша оптимизированы под проект

3. **C3 (★★2): Секреты для разных окружений**
   - Разграничение по окружениям: dev, staging, production
   - Маскирование секретов в логах (`::add-mask::`)
   - GitHub Secrets для каждого окружения
   - GitHub Environments для контроля доступа

4. **C4 (★★2): Релевантные артефакты**
   - Coverage HTML отчёты для каждой версии Python/OS
   - Test reports (JUnit XML)
   - Lint reports (ruff, black, isort)
   - Docker образ сохраняется как артефакт
   - Все артефакты хранятся 30 дней

5. **C5 (★★2): CD/промоушн (мок-деплой)**
   - Staging deployment при push в `staging` ветку
   - Production deployment при push в `main`
   - GitHub Pages для документации API
   - Manual deployment через workflow_dispatch

## P08 Чек-лист — Доказательства выполнения (★★2 на оценку 10)

### C1. Сборка и тесты (★★2)

**Настроена матрица (несколько версий Python/OS), кэш зависимостей и параллельные шаги:**

**Матрица сборки:**
```yaml
strategy:
  matrix:
    python-version: ["3.11", "3.12"]
    os: [ubuntu-latest, windows-latest]
```

**Параллельные шаги:**
- `build-and-test` — запускается параллельно для всех комбинаций Python/OS
- `build-docker` — параллельно со сборкой тестов
- `container-security` — параллельно после сборки Docker

**Кэш зависимостей:**
- Используется встроенный кэш `actions/setup-python@v5` с `cache: 'pip'`
- Дополнительный кэш по хешу requirements.txt

**Доказательства:**
- Лог CI run: [GitHub Actions](https://github.com/sirMatras/course-project-sirMatras-/actions)
- Workflow файл: [.github/workflows/ci-cd.yml](.github/workflows/ci-cd.yml)
- Все комбинации Python/OS проходят успешно

---

### C2. Кэширование/конкурренси (★★2)

**Оптимизированы ключи кэша под свой проект:**

**Кэш pip зависимостей:**
```yaml
key: ${{ runner.os }}-pip-${{ matrix.cache-key }}-${{ hashFiles('requirements.txt', 'requirements-dev.txt') }}
```
- Кэш инвалидируется при изменении requirements.txt
- Разные ключи для разных версий Python и OS

**Кэш pyproject.toml:**
```yaml
key: ${{ runner.os }}-python-${{ matrix.python-version }}-${{ hashFiles('pyproject.toml') }}
```
- Кэш для Python пакетов по pyproject.toml

**Docker layer cache:**
```yaml
cache-from: type=gha
cache-to: type=gha,mode=max
```
- GitHub Actions cache для Docker слоёв
- Ускоряет пересборку образа

**Concurrency:**
```yaml
concurrency:
  group: ci-${{ github.ref }}-${{ github.workflow }}
  cancel-in-progress: true
```
- Предотвращает дубликаты запусков
- Отменяет старые запуски при новом push

**Доказательства:**
- Diff workflow: [.github/workflows/ci-cd.yml](.github/workflows/ci-cd.yml)
- Кэш ключи оптимизированы под структуру проекта
- Docker cache использует GitHub Actions cache backend

---

### C3. Секреты и конфиги (★★2)

**Настроены секреты/vars для своего окружения с разграничением ролей/окружений:**

**GitHub Secrets для разных окружений:**

**Development (CI):**
- `DATABASE_URL_DEV` — для тестов в CI
- `JWT_SECRET_DEV` — для тестов

**Staging:**
- `DATABASE_URL_STAGING` — staging база данных
- `JWT_SECRET_STAGING` — staging JWT секрет
- `POSTGRES_PASSWORD_STAGING` — пароль БД

**Production:**
- `DATABASE_URL_PRODUCTION` — production база данных
- `JWT_SECRET_PRODUCTION` — production JWT секрет
- `POSTGRES_PASSWORD_PRODUCTION` — пароль БД

**Маскирование в логах:**
```yaml
run: |
  echo "::add-mask::$DATABASE_URL"
  echo "::add-mask::$JWT_SECRET"
```
- Все секреты маскируются в логах CI
- Не видны в выводе команд

**GitHub Environments:**
- `staging` — для staging деплоя
- `production` — для production деплоя
- Контроль доступа через GitHub Environments

**Доказательства:**
- Workflow использует `${{ secrets.* }}` для всех секретов
- Маскирование через `::add-mask::`
- Разные секреты для dev/staging/production
- Скрин настроек Secrets (без значений) — нужно добавить в PR

---

### C4. Артефакты/репорты (★★2)

**Артефакты релевантны своему проекту и используются при релизе:**

**Coverage отчёты:**
- HTML отчёты для каждой версии Python/OS
- XML отчёты для интеграции с инструментами
- Сохраняются как артефакты на 30 дней

**Test reports:**
- JUnit XML формат для интеграции
- Доступны в артефактах CI

**Lint reports:**
- Ruff отчёт (ruff-report.txt)
- Black diff отчёт (black-report.txt)
- isort diff отчёт (isort-report.txt)

**Docker образ:**
- Сохраняется как артефакт для PR
- Публикуется в GitHub Container Registry для main/staging
- Используется при деплое

**Сводный отчёт:**
- `ci-summary.md` с результатами всех проверок
- Доступен в артефактах

**Доказательства:**
- CI run → Artifacts: доступны после каждого запуска
- Артефакты хранятся 30 дней
- Docker образ доступен в GitHub Container Registry
- Coverage HTML отчёты можно просмотреть локально

---

### C5. CD/промоушн (эмуляция) (★★2)

**Настроен промоушн/мок-деплой под свой стенд/окружение:**

**Staging deployment:**
- Триггер: push в `staging` ветку или workflow_dispatch
- Использует секреты `*_STAGING`
- Мок-деплой с логированием шагов
- Environment: `staging` с URL

**Production deployment:**
- Триггер: push в `main` или workflow_dispatch
- Использует секреты `*_PRODUCTION`
- Требует прохождения всех проверок
- Environment: `production` с URL

**GitHub Pages:**
- Автоматический деплой документации при push в `main`
- Генерируется API документация
- Доступна по адресу: `https://sirMatras.github.io/course-project-sirMatras-/`

**Manual deployment:**
- `workflow_dispatch` с выбором окружения
- Позволяет запустить деплой вручную

**Доказательства:**
- CI run с шагами CD: `deploy-staging`, `deploy-production`, `deploy-docs`
- Конфиг деплоя в workflow файле
- Логи показывают мок-деплой с описанием реальных шагов

---

## Технические детали

### Матрица сборки (C1 ★★2):

**Комбинации:**
- Python 3.11 на Ubuntu
- Python 3.12 на Ubuntu
- Python 3.11 на Windows
- Python 3.12 на Windows

**Параллельность:**
- Все комбинации запускаются параллельно
- `fail-fast: false` — все версии проверяются даже при ошибке в одной

### Кэширование (C2 ★★2):

**Стратегия кэша:**
1. **Pip кэш:** по хешу requirements.txt + requirements-dev.txt
2. **Python кэш:** по хешу pyproject.toml
3. **Docker кэш:** GitHub Actions cache (type=gha)
4. **Встроенный кэш:** actions/setup-python с cache: 'pip'

**Ключи кэша:**
- Уникальные для каждой комбинации OS + Python версии
- Инвалидация при изменении зависимостей
- Восстановление из предыдущих коммитов

### Секреты (C3 ★★2):

**Структура секретов:**
```
DATABASE_URL_DEV / STAGING / PRODUCTION
JWT_SECRET_DEV / STAGING / PRODUCTION
POSTGRES_PASSWORD_STAGING / PRODUCTION
```

**Маскирование:**
- Все секреты маскируются через `::add-mask::`
- Не отображаются в логах CI
- Безопасный вывод в консоль

**Environments:**
- GitHub Environments для staging и production
- Контроль доступа через GitHub
- Защита production окружения

### Артефакты (C4 ★★2):

**Типы артефактов:**
1. **Coverage:** HTML + XML отчёты
2. **Test reports:** JUnit XML
3. **Lint reports:** текстовые отчёты
4. **Docker image:** tar архив образа
5. **Summary:** сводный отчёт

**Использование:**
- Coverage HTML можно скачать и открыть локально
- Test reports для интеграции с инструментами
- Docker образ используется при деплое

### CD/деплой (C5 ★★2):

**Staging:**
- Автоматический деплой при push в `staging`
- Мок-деплой с описанием реальных шагов
- Использует staging секреты

**Production:**
- Автоматический деплой при push в `main`
- Требует прохождения всех проверок
- Использует production секреты

**GitHub Pages:**
- Автоматическая генерация документации
- Деплой при каждом push в `main`
- Доступна публично

---

## Изменённые файлы

### Новые файлы:
- `.github/workflows/ci-cd.yml` — основной CI/CD pipeline с матрицей и деплоем

### Изменённые файлы:
- `.github/workflows/ci.yml` — оставлен для обратной совместимости (P07 проверки)

---

## Результаты проверок

### CI Run:
- ✅ Все комбинации Python/OS проходят успешно
- ✅ Docker образ собирается и публикуется
- ✅ Тесты проходят на всех платформах
- ✅ Coverage отчёты генерируются

### Артефакты:
- ✅ Coverage HTML отчёты доступны
- ✅ Test reports (JUnit XML) доступны
- ✅ Lint reports доступны
- ✅ Docker образ доступен в registry

### Деплой:
- ✅ Staging deployment работает (мок)
- ✅ Production deployment работает (мок)
- ✅ GitHub Pages деплоится автоматически

---

## Настройка GitHub Secrets

Для полноценной работы CI/CD необходимо настроить следующие секреты в GitHub:

### Development (для CI тестов):
- `DATABASE_URL_DEV` — SQLite или тестовая БД
- `JWT_SECRET_DEV` — тестовый секрет

### Staging:
- `DATABASE_URL_STAGING` — staging база данных
- `JWT_SECRET_STAGING` — staging JWT секрет
- `POSTGRES_PASSWORD_STAGING` — пароль БД

### Production:
- `DATABASE_URL_PRODUCTION` — production база данных
- `JWT_SECRET_PRODUCTION` — production JWT секрет
- `POSTGRES_PASSWORD_PRODUCTION` — пароль БД

**Настройка:**
1. Перейти в Settings → Secrets and variables → Actions
2. Добавить секреты для каждого окружения
3. Настроить Environments (staging, production) для контроля доступа

---

## Выводы

1. **Матрица сборки:** Проверка на Python 3.11, 3.12 на Ubuntu и Windows
2. **Кэширование:** Оптимизированные ключи кэша ускоряют сборку
3. **Секреты:** Разграничение по окружениям с маскированием
4. **Артефакты:** Релевантные отчёты для анализа и деплоя
5. **CD:** Автоматический деплой в staging и production с мок-реализацией

---

## Ссылки

- [CI/CD Workflow](.github/workflows/ci-cd.yml)
- [GitHub Actions](https://github.com/sirMatras/course-project-sirMatras-/actions)
- [GitHub Container Registry](https://github.com/sirMatras/course-project-sirMatras-/pkgs/container/workout-log-api)

