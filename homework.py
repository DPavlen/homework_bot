import logging
import os
import requests

from telegram import ReplyKeyboardMarkup
from telegram.ext import CommandHandler, Updater

from dotenv import load_dotenv
load_dotenv()

# secret_token = os.getenv('TOKEN')
PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens():
    """Проверка доступности переменных окружения,
    которые необходимы для работы программы."""
    ...


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат, 
    определяемый переменной окружения TELEGRAM_CHAT_ID."""
    ...


def get_api_answer(timestamp):
    """Делает запрос к единственному эндпоинту API-сервиса."""
    ...


def check_response(response):
    """Проверяет ответ API на соответствие документации
    из урока API сервиса Практикум.Домашка."""
    ...


def parse_status(homework):
    """Извлекает из информации о конкретной 
    домашней работе статус этой работы."""
    ...

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""

    ...

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())

    ...

    while True:
        try:

            ...

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            ...
        ...


if __name__ == '__main__':
    main()
