import json
import logging
import os
import time
import requests

from http import HTTPStatus
from logging.handlers import RotatingFileHandler
from sys import exit as kill_bot
from telegram import Bot, TelegramError

from dotenv import load_dotenv

from exceptions_api_answer import (StatusOtherThan200Error,
                                   ApiRequestError,
                                   # UnexpectedError,
                                   JSONDecodeError,
                                   EmptyResponseFromAPI,
                                   )

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
    # Создадим словарь токенов и переберем в цикле c флагом
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
    """Делает запрос к единственному эндпоинту API-сервиса.
    Получение ответа от Яндекс-Практикума."""
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

    except json.JSONDecodeError as error_json:
        msg_error = f'Ошибка при преобразовании JSON: {error_json}'
        raise JSONDecodeError(msg_error)


def check_response(response):
    """Проверяет ответ API на соответствие документации
    из урока API сервиса Практикум.Домашка."""
    logging.debug('Начало проверки Домашки')

    if not isinstance(response, dict):
        raise TypeError('Ошибка в типе ответа API')

    if 'homeworks' not in response:
        raise EmptyResponseFromAPI('Пустой ответ от API')

    homeworks = response.get('homeworks')
    if not isinstance(homeworks, list):
        raise KeyError('Homeworks не является списком')
    return homeworks


def parse_status(homework):
    """Извлекает из информации о конкретной
    домашней работе статус этой работы."""
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
        raise ValueError(message)

    verdict = HOMEWORK_VERDICTS[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    check_tokens()
    bot = Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())

    ...

    while True:
        try:
            response = get_api_answer(timestamp)
            timestamp = response.get('current_date')
            # homeworks = response.get('homeworks')
            check_response(response)
            logger.debug('Запрос проверен.')

            ...
        except TelegramError as error:
            logger.error(f'Сообщение не удалось отправить! {error}')

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
    main()
