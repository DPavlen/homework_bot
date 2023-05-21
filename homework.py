import logging
import os
import requests

from logging.handlers import RotatingFileHandler
from telegram import ReplyKeyboardMarkup
from telegram.ext import CommandHandler, Updater
from sys import exit as kill_bot
from telegram import Bot, TelegramError

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

# А тут установлены настройки логгера для текущего файла - example_for_log.py
logger = logging.getLogger(__name__)
# Здесь задана глобальная конфигурация для всех логгеров
logging.basicConfig(
    level=logging.DEBUG,
    filename='program.log',
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s'
)
# Создаем форматер
formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'
)
# Указываем обработчик логов
handler = RotatingFileHandler(
    'bot.log',
    maxBytes=50000000,
    encoding='UTF-8'
    # backupCount=5,
)

handler.setFormatter(formatter)
logger.addHandler(handler)


def check_tokens():
    """Проверка доступности переменных окружения,
    которые необходимы для работы программы."""
    # Создадим словарь токенов и переберем в цикле
    names_tokens = {
        'PRACTICUM_TOKEN': PRACTICUM_TOKEN,
        'TELEGRAM_TOKEN': TELEGRAM_TOKEN,
        'TELEGRAM_CHAT_ID': TELEGRAM_CHAT_ID,
    }
    token_flag = False
    for name_token, token in names_tokens.items():
        if not token:
            token_flag = True
            erorr_tokens = ('Бот не смог отправить сообщение')
            no_tokens_msg = (f'Бот не работает!'
                             f'Отсутствует переменная окружения:{name_token}!')
            logger.error(erorr_tokens)
            logger.critical(no_tokens_msg)
    if token_flag:
        kill_bot(no_tokens_msg)


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат,
    определяемый переменной окружения TELEGRAM_CHAT_ID."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.info(f'Отправляет сообщение пользователю:{message}')
    except TelegramError as telegram_error:
        logger.error(f'Сообщение в Telegram не отправлено: {telegram_error}')


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
