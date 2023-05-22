import logging
import os
import time
from http import HTTPStatus
from logging.handlers import RotatingFileHandler
from sys import exit

import requests
from dotenv import load_dotenv
from telegram import Bot, TelegramError

from exceptions_api_answer import (StatusOtherThan200Error,
                                   ApiRequestError,
                                   )

load_dotenv()

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

logger = logging.getLogger(__name__)
formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'
)
handler = RotatingFileHandler(
    'bot.log',
    maxBytes=50000000,
    encoding='UTF-8'
)
handler.setFormatter(formatter)
logger.addHandler(handler)


def check_tokens():
    """Проверка доступности переменных окружения."""
    names_tokens = {
        'PRACTICUM_TOKEN': PRACTICUM_TOKEN,
        'TELEGRAM_TOKEN': TELEGRAM_TOKEN,
        'TELEGRAM_CHAT_ID': TELEGRAM_CHAT_ID,
    }
    is_token: bool = False
    for name_token, token in names_tokens.items():
        if not token:
            is_token = True
            no_tokens_msg = (f'Бот не работает!'
                             f'Отсутствует переменная окружения:{name_token}!')
            logger.critical(no_tokens_msg)
    if is_token:
        exit(no_tokens_msg)


def send_message(bot, message):
    """Отправка сообщения в чат, определяемая TELEGRAM_CHAT_ID."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.debug(f'Отправляет сообщение пользователю:{message}')
    except TelegramError as telegram_error:
        logger.error(f'Сообщение в Telegram не отправлено: {telegram_error}')


def get_api_answer(timestamp):
    """Получение ответа от Яндекс-Практикума."""
    try:
        api_answer_yandex = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params={'from_date': timestamp}
        )
        logger.debug('Отправка запроса.')
        if api_answer_yandex.status_code != HTTPStatus.OK:
            msg_error = (f'API Эндпойнт{ENDPOINT} в данный момент недоступен, '
                         f'код ошибки: {api_answer_yandex.status_code}')
            raise StatusOtherThan200Error(msg_error)
        logger.debug('Запрос успешно отправлен.')

        return api_answer_yandex.json()

    except requests.exceptions.RequestException as error_request:
        msg_error = f'Ошибка при запросе к API: {error_request}'
        raise ApiRequestError(msg_error)


def check_response(response):
    """Проверяет ответ API на соответствие документации."""
    if not isinstance(response, dict):
        msg = 'Ошибка в типе ответа API'
        logger.error(msg)
        raise TypeError(msg)

    if 'homeworks' not in response:
        msg = 'Нет ключа в ответе API'
        logger.error(msg)
        raise KeyError(msg)

    homeworks = response.get('homeworks')
    if not isinstance(homeworks, list):
        msg = ('Проверка ответа API списка')
        logger.error(msg)
        raise TypeError(msg)
    return homeworks


def parse_status(homework):
    """Информация о домашней работе и ее статус."""
    homework_all = ('homework_name', 'status')
    for homework_key in homework_all:
        if homework_key not in homework:
            message = f'В ответе API отсутсвует ключ "{homework_key}".'
            logger.error(message)
            raise KeyError(message)

    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')

    if homework_status not in HOMEWORK_VERDICTS:
        message = f'Неизвестный статус работы ревью: {homework_status}'
        raise KeyError(message)

    verdict = HOMEWORK_VERDICTS[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    check_tokens()
    bot = Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    current_report = {
        'name': '',
        'output': ''
    }

    while True:
        try:
            response = get_api_answer(timestamp)
            timestamp = response.get('current_date')
            new_homeworks = response.get('homeworks')
            check_response(response)
            logger.debug('Запрос проверен.')
            if new_homeworks:
                homework, *_ = new_homeworks
                message = parse_status(homework)
                current_report['name'] = homework.get('homework_name')
                current_report['output'] = homework.get('status')
                send_message(bot, message)
                logger.debug(f'Пользователю отправлено: {message}')
            else:
                current_report['output'] = 'Новых статусов работ Нет!'
                logger.debug(current_report['output'])

        except Exception as error:
            last_error = ''
            message = f'Сбой в работе программы: {error}'
            logger.error(message, error)
            if message != last_error:
                last_error = message
                send_message(bot, message)
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        filename='program.log',
        format='%(asctime)s, %(levelname)s, %(message)s, %(name)s'
    )
    main()
