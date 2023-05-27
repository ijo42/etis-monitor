# Бот для мониторинга статуса веб-сайта [WIP]
* Каждый час скрипт опрашивает сайт по его `http status-code`, если таковой изменился - в телеграм канал уходит уведомление

## Setup:
1. [Создать бота](https://t.me/BotFather), токен передать в config
2. Создать канал, добавить бота с правами администратора
3. Получить chat_id канала, передать в config
4. Переименовать `config_example` -> `config`
5. Установить зависимости (`pip install -r requirements.txt`)
6. Помочь проекту
7. Запустить скрипт `python ./main.py`

## Запуск под Docker (linux only):
1. создать бд и лог-файл `touch logging.log base.db`
2. docker compose up -d

##### tg channel: https://t.me/etis_monitor