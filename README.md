# WB Service

Сервис для работы с заказами и поставками Wildberries через Telegram-бота.

## Структура

```text
app/
  main.py                 # точка входа приложения
  bot/                    # Telegram-слой
  services/               # бизнес-сценарии
  clients/                # клиенты внешних API
  repositories/           # слой доступа к SQLite
  config/                 # настройки и пути проекта
scripts/
  init_db.py              # создание таблиц SQLite
data/
  database.sqlite3        # рабочая база данных
uploads/
  .gitkeep                # временные файлы, загруженные в бот
```

## Установка

```bash
pip install -r requirements.txt
```

## Слои

- `app/clients/wildberries_client.py` - все HTTP-запросы к Wildberries.
- `app/repositories/database.py` - подключение к SQLite.
- `app/repositories/tasks_repository.py` - таблица `tasks`.
- `app/repositories/supplies_repository.py` - таблица `supplies`.
- `app/repositories/article_supply_repository.py` - таблица `art_supp`.
- `app/services/sorting_service.py` - сценарии пересортировки и работы с поставками.
- `app/services/orders_service.py` - получение новых заказов и обновление таблицы `tasks`.
- `app/services/supplies_service.py` - работа с поставками и заказами внутри поставок.
- `app/services/article_supply_service.py` - связки артикулов с названиями поставок.
- `app/services/excel_import_service.py` - чтение Excel и обновление связок артикулов с поставками.
- `app/bot/bot.py` - сборка Telegram-приложения и регистрация обработчиков.
- `app/bot/handlers.py` - обработчики команд, кнопок и файлов.
- `app/bot/keyboards.py` - клавиатуры Telegram.
- `app/bot/messages.py` - тексты кнопок и ответов.

## Следующий этап рефакторинга

1. После переписывания Telegram-бота поправить тексты в `app/bot/messages.py`.
2. Добавить нормальную обработку ошибок API и логирование в сервисном слое.
