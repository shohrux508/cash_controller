# CashController 💰

Telegram-бот для быстрого учёта личных и семейных финансов.

**Быстрый ввод** — просто напиши в чат:
```
-25 такси       →  расход 25 000 сум
+150 зарплата   →  доход 150 000 сум
-3.5 кофе       →  расход 3 500 сум
```

Число автоматически умножается на 1 000. Категория определяется по описанию.

---

## Возможности

- 🚀 **Быстрый ввод** — `+25 зарплата`, `-15 такси`
- 📊 **Статистика** — за день, неделю, месяц с разбивкой по категориям
- 📋 **История** — последние записи, отмена последней
- 📁 **Категории** — автоматическое определение + свои
- ⏰ **Напоминания** — настраиваемые по расписанию
- 👨‍👩‍👧‍👦 **Семейный доступ** — whitelist по Telegram ID
- 🌐 **REST API** — готов для WebApp

## Быстрый старт

### 1. Установка

```bash
# Клонировать и установить зависимости
git clone <repo-url> cash_controller
cd cash_controller
uv sync --all-extras

# Настроить переменные окружения
cp .env.example .env
# Отредактировать .env — указать BOT_TOKEN и ADMIN_CHAT_IDS
```

### 2. Получить BOT_TOKEN

1. Открой [@BotFather](https://t.me/BotFather) в Telegram
2. Отправь `/newbot`, выбери имя
3. Скопируй токен в `.env`

### 3. Узнать свой Telegram ID

1. Открой [@userinfobot](https://t.me/userinfobot) в Telegram
2. Скопируй ID в `ADMIN_CHAT_IDS` в `.env`

### 4. Запуск

```bash
uv run python main.py
```

Бот и API запустятся одновременно:
- Telegram бот — polling
- REST API — http://localhost:8000/docs

---

## Команды бота

| Команда | Описание |
|---------|----------|
| `/start` | Приветствие и инструкция |
| `/help` | Полная справка |
| `/today` | Итоги за сегодня |
| `/week` | Итоги за неделю |
| `/month` | Итоги за месяц |
| `/history` | Последние 10 записей |
| `/undo` | Удалить последнюю запись |
| `/categories` | Список категорий |
| `/reminder 21:00` | Установить напоминание |
| `/reminder off` | Отключить напоминание |
| `/reminder` | Проверить статус |

---

## Конфигурация (.env)

| Переменная | Описание | По умолчанию |
|------------|----------|-------------|
| `APP_NAME` | Название | `cash-controller` |
| `DEBUG` | Режим отладки | `false` |
| `DATABASE_URL` | URL базы данных | `sqlite+aiosqlite:///./dev.db` |
| `BOT_TOKEN` | Токен бота (обязательно) | — |
| `ADMIN_CHAT_IDS` | Telegram ID пользователей | `[]` |
| `LOG_LEVEL` | Уровень логов | `INFO` |

---

## Структура проекта

```
cash_controller/
├── app/
│   ├── api/v1/              # REST API эндпоинты
│   │   ├── health.py        # GET /api/v1/health/
│   │   └── transactions.py  # CRUD транзакций
│   ├── bot/                 # Telegram бот (Aiogram 3)
│   │   ├── handlers/        # Обработчики команд
│   │   ├── middlewares/      # Auth middleware
│   │   ├── keyboards/       # Inline клавиатуры
│   │   ├── scheduler.py     # APScheduler (напоминания)
│   │   └── utils.py         # Форматирование
│   ├── core/                # Конфигурация
│   │   ├── config.py        # Settings
│   │   └── container.py     # Lifespan, Bot + FastAPI
│   ├── database/            # SQLAlchemy ORM
│   │   ├── engine.py        # Async engine
│   │   └── models.py        # User, Category, Transaction, Reminder
│   └── services/            # Бизнес-логика
│       ├── user_service.py
│       ├── category_service.py
│       ├── transaction_service.py
│       └── reminder_service.py
├── tests/
├── Dockerfile
├── docker-compose.yml
└── pyproject.toml
```

---

## Деплой (Docker / Railway)

```bash
# Docker
docker-compose up --build

# Railway
# 1. Подключить репозиторий
# 2. Добавить переменные: BOT_TOKEN, ADMIN_CHAT_IDS, DATABASE_URL
# 3. Добавить volume для /app/data (SQLite persistence)
```

---

## Стек технологий

| Категория | Инструменты |
|-----------|------------|
| Bot | Aiogram 3, APScheduler |
| Web | FastAPI, Uvicorn |
| Данные | SQLAlchemy 2.0 (async), aiosqlite |
| Конфигурация | pydantic-settings |
| Логи | Loguru |
| Инфраструктура | Docker, uv |
