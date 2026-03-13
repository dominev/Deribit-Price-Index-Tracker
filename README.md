# Deribit Price Index Tracker

Сервис для периодического сбора индексных цен криптовалют с биржи Deribit и предоставления доступа к данным через REST API.

---

## Содержание

- [Технологический стек](#технологический-стек)
- [Архитектура](#архитектура)
- [Требования](#требования)
- [Установка и запуск](#установка-и-запуск)
- [Переменные окружения](#переменные-окружения)
- [API](#api)
- [Тестирование](#тестирование)
- [Возможные улучшения](#возможные-улучшения)
- [Лицензия](#лицензия)

---

## Технологический стек

| Компонент           | Технология                                      |
|---------------------|--------------------------------------------------------|
| Язык                | Python 3.11+                                           |
| Web-фреймворк       | FastAPI                                                |
| База данных         | PostgreSQL                                             |
| ORM                 | SQLAlchemy 2.0 (asyncio) + asyncpg                     |
| Фоновые задачи      | Celery + Redis                                         |
| HTTP-клиент         | aiohttp                                                |
| Контейнеризация     | Docker, docker-compose                                 |
| Тестирование        | pytest (Тесты удалены, использовалить только при создании проекта)|

---

## Архитектура
```
deribit-price-tracker/
│
├── 📁 app/ # Основной код приложения
│ ├── 📁 api/ # HTTP эндпоинты
│ │ └── prices.py # Маршруты для работы с ценами
│ │
│ ├─── 📁 repositories/ # Доступ к данным
│ │ └── price_repository.py # Работа с таблицей цен
│ │
│ ├── 📁 services/ # Бизнес-логика
│ │ ├── deribit_client.py # Deribit API
│ │ └── price_service.py # Сервис для работы с ценами
│ │
│ ├── 📁 tasks/ # Celery задачи
│ │ └── fetch_prices.py # Периодический сбор цен
│ │
│ ├──── 📄 config.py # Настройки из переменных окружения
│ ├──── 📄 database.py # Postgresql database
│ ├──── 📄 dependencies.py # Зависимости для маршрутов 
│ ├──── 📄 main.py # Точка входа FastAPI
│ ├──── 📄 models.py # SQLAlchemy
│ └──── 📄 shemas.py # Pydantic схемы
│ 
├── 📄 docker-compose.yml # Контейнеры
├── 📄 Dockerfile # Сборка образа приложения
├── 📄 requirements.txt # Зависимости Python
├── 📄 .env.example # Переменные окружения
└── 📄 README.md # Документация
```

## Design decisions
#### Ключевые решения

- **Чистая архитектура**: разделение ответственности между слоями (роуты → сервисы → репозитории). Внедрение зависимостей через `Depends`.
- **Асинхронность**: полный стек `async/await` — от HTTP-запросов до работы с БД.
- **Плавное завершение работы**: корректное закрытие соединений (`aiohttp`, PostgreSQL) через `lifespan` FastAPI.
- **Ограничение запросов**: `asyncio.Semaphore` для ограничения запросов к Deribit API (5 запросов/секунду).
- **Логика задержки**: декоратор `tenacity` с экспоненциальной задержкой для обработки сетевых ошибок.
- **Индексы БД**: составной индекс `(ticker, timestamp)` для оптимизации выборок по диапазону дат.
- **Логирование**: централизованная настройка через модуль `logging`, уровень определяется переменной окружения.
- **Контейнеризация**: все сервисы (app, worker, beat, db, redis) формируются через `docker-compose`.

---

## Для установки и запуска потребуется:

*Docker Desktop* - https://www.docker.com/products/docker-desktop/

*Git* - https://git-scm.com/install/windows

## Дальнейшие шаги
### 1. Клонирование репозитория

```bash

git clone https://github.com/dominev/deribit-price-index-tracker
cd deribit-price-index-tracker

```

### 2. Настройка окружения

```bash

cp .env.example .env

```

> При необходимости отредактируйте значения в .env

### 3. Запуск сервисов

```bash

docker-compose up -d

```

> Первый запуск требует 5–10 минут для загрузки образов и инициализации БД.

### 4. Проверка работоспособности

- Документация API: [http://localhost:8000/docs](http://localhost:8000/docs)
- Последняя цена BTC/USD: [http://localhost:8000/prices/latest?ticker=btc_usd](http://localhost:8000/prices/latest?ticker=btc_usd)
- Последняя цена ETH/USD: [http://localhost:8000/prices/latest?ticker=eth_usd](http://localhost:8000/prices/latest?ticker=eth_usd)

### Управление сервисами

*Остановка*
```bash
docker-compose down
```
*Просмотр логов*
```bash
docker-compose logs -f app
```
*Перезапуск после изменений*
```bash
docker-compose up -d --build
```

---

## Переменные окружения

| Переменная         | Описание                             | Значение по умолчанию                         |
|--------------------|--------------------------------------|-----------------------------------------------|
| `DATABASE_URL`     | Строка подключения к PostgreSQL      | `postgresql+asyncpg://user:pass@db:5432/deribit` |
| `REDIS_URL`        | Строка подключения к Redis           | `redis://redis:6379/0`                        |
| `DERIBIT_API_URL`  | Endpoint Deribit API                 | `https://www.deribit.com/api/v2/public`       |
| `FETCH_INTERVAL`   | Интервал опроса цен (сек)            | `60`                                          |
| `RATE_LIMIT`       | Макс. запросов к Deribit в секунду   | `5`                                           |
| `LOG_LEVEL`        | Уровень логирования                  | `INFO`                                        |
| `API_HOST`         | Хост для FastAPI                     | `0.0.0.0`                                     |
| `API_PORT`         | Порт для FastAPI                     | `8000`                                        |

---

## API

### Параметры запросов

Все эндпоинты требуют обязательный параметр `ticker` в формате `{base}_{quote}` (например, `btc_usd`, `eth_usd`).

### Эндпоинты

#### Получить все записи по тикеру

**GET** `/prices?ticker=btc_usd&limit=100&offset=0`

**Параметры:**
- `ticker` (required) — идентификатор торговой пары
- `limit` (optional) — количество записей (по умолчанию: 100)
- `offset` (optional) — смещение для пагинации

**Ответ:**
json [ { "id": 42, "ticker": "btc_usd", "price": 26450.12, "timestamp": 1693526400 } ]

---

#### Получить последнюю цену

**GET** `/prices/latest?ticker=eth_usd`

**Ответ:**
json { "id": 157, "ticker": "eth_usd", "price": 1632.45, "timestamp": 1693872000 }

---

#### Получить цены за период

**GET** `/prices/filter?ticker=btc_usd&from_date=1693526400&to_date=1693872000`

**Параметры:**
- `from_date` — начало периода (UNIX timestamp, секунды)
- `to_date` — конец периода (UNIX timestamp, секунды)

**Ответ:** массив объектов, аналогичный эндпоинту `/prices`.

---

### Коды ответов

| Код | Описание                     |
|-----|------------------------------|
| 200 | Успешный запрос              |
| 400 | Некорректные параметры запроса |
| 404 | Данные по тикеру не найдены   |
| 500 | Внутренняя ошибка сервера     |

---

## Тестирование
Изначально в проекте были тесты, но удалены для переписывания (будут добавлены позже).
Основной функционал можно проверить через UI: http://localhost:8000/docs

## Лицензия

MIT License
