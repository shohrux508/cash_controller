# backend-template

Промышленный шаблон для быстрого развертывания серверной экосистемы на FastAPI.

Минималистичный, строго типизированный каркас — только чистый REST API, готовый к масштабированию.

---

## Быстрый старт

### Локально (uv)

```bash
# Установить зависимости (включая dev)
uv sync --all-extras

# Скопировать переменные окружения
cp .env.example .env

# Запустить сервер
uv run python main.py

# Открыть документацию: http://localhost:8000/docs
```

### Docker

```bash
# Скопировать переменные окружения
cp .env.example .env

# Собрать и запустить (app + PostgreSQL)
docker-compose up --build
```

---

## Структура проекта

```
backend-template/
├── app/
│   ├── api/                # Эндпоинты, роутеры, зависимости FastAPI
│   │   ├── deps.py         # Depends: get_session
│   │   └── v1/
│   │       └── health.py   # GET /api/v1/health/
│   ├── core/               # Конфигурация и оркестратор приложения
│   │   ├── config.py       # Settings (pydantic-settings)
│   │   └── container.py    # AppContainer + lifespan + create_app()
│   ├── database/           # Подключение к БД и ORM-модели
│   │   ├── engine.py       # AsyncEngine, async_sessionmaker
│   │   └── models.py       # Base, TimestampMixin
│   ├── services/           # Слой бизнес-логики (заготовка)
│   └── logger.py           # Loguru + перехват stdlib логов
├── migrations/             # Alembic (async, render_as_batch=True)
├── scripts/
│   └── run_checks.py       # Единый конвейер качества
├── tests/                  # pytest-asyncio + in-memory SQLite
├── main.py                 # Точка входа (Windows event loop fix)
├── pyproject.toml          # Зависимости, ruff, mypy, pytest
├── Dockerfile              # Multi-stage (python:3.12-slim + uv)
└── docker-compose.yml      # app + PostgreSQL 16
```

---

## Конфигурация (.env)

| Переменная      | Описание                      | По умолчанию                      |
|-----------------|-------------------------------|-----------------------------------|
| `APP_NAME`      | Название приложения           | `backend-template`                |
| `DEBUG`         | Режим отладки                 | `false`                           |
| `DATABASE_URL`  | URL базы данных               | `sqlite+aiosqlite:///./dev.db`    |
| `LOG_LEVEL`     | Уровень логирования           | `INFO`                            |
| `LOG_FORMAT`    | Формат логов (`text` / `json`)| `text`                            |
| `CORS_ORIGINS`  | Разрешённые origins           | `*`                               |

---

## Миграции (Alembic)

```bash
# Создать миграцию
uv run alembic revision --autogenerate -m "описание"

# Применить миграции
uv run alembic upgrade head

# Откатить на одну
uv run alembic downgrade -1
```

---

## Проверка качества

```bash
# Запустить все проверки одной командой
uv run python scripts/run_checks.py
```

Конвейер выполняет:
1. **ruff check** — линтинг
2. **ruff format** — форматирование
3. **mypy --strict** — статическая типизация
4. **pytest --cov** — тесты с покрытием

---

## Стек технологий

| Категория     | Инструменты                                        |
|---------------|----------------------------------------------------|
| Web           | FastAPI, Uvicorn, httpx                            |
| Данные        | SQLAlchemy ≥ 2.0 (async), aiosqlite, asyncpg, Alembic |
| Конфигурация  | pydantic-settings, python-dotenv                   |
| Логи          | Loguru (JSON + text, перехват stdlib)               |
| Качество      | ruff, mypy (strict), pytest, pytest-cov            |
| Инфраструктура| Docker (multi-stage), docker-compose               |
| Пакеты        | uv                                                 |
