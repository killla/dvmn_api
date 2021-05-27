import os
import time
import logging

import requests
import telegram
from dotenv import load_dotenv


logger = logging.getLogger(__name__)


def send_messages(messages, bot, tg_chat_id, site):
    for message in messages:
        lesson_title = message['lesson_title']
        lesson_url = message['lesson_url']
        is_negative = message['is_negative']
        send_tg_message(lesson_title, lesson_url, is_negative, bot, tg_chat_id, site)


def send_tg_message(title, url, is_negative, bot, tg_chat_id, site):
    text = f'У вас проверили работу «{title}»\n{site}{url}'
    if is_negative:
        text = text + '\n\nК сожалению, в работе нашлись ошибки.'
    else:
        text = text + '\n\nПреподавателю всё понравилось.'
    bot.send_message(chat_id=tg_chat_id, text=text)


def main():
    load_dotenv()
    log_level = os.getenv("LOG_LEVEL")
    bot_token = os.getenv("BOT_TOKEN")
    log_bot_token = os.getenv("LOG_BOT_TOKEN")
    dvmn_token = os.getenv("DVMN_TOKEN")
    tg_chat_id = os.getenv("TG_CHAT_ID")
    site = 'https://dvmn.org'
    api_url = 'https://dvmn.org/api/long_polling/'
    bot = telegram.Bot(token=bot_token)
    log_bot = telegram.Bot(token=log_bot_token)

    logger.setLevel(log_level)


    class MyLogsHandler(logging.Handler):
        def emit(self, record):
            log_entry = self.format(record)
            log_bot.send_message(chat_id=tg_chat_id, text=log_entry)


    logger.addHandler(MyLogsHandler())

    logger.info('Бот запущен')
    payload = {'timestamp_to_request': ''}
    headers = {'Authorization': f'Token {dvmn_token}'}
    while True:
        try:
            response = requests.get(api_url, headers=headers, params=payload)
            response.raise_for_status()
            server_response = response.json()
            if server_response['status'] == 'found':
                payload = {'timestamp': server_response['last_attempt_timestamp']}
                messages = server_response['new_attempts']
                send_messages(messages, bot, tg_chat_id, site)
            elif server_response['status'] == 'timeout':
                payload = {'timestamp': server_response['timestamp_to_request']}
        except requests.exceptions.ReadTimeout:
            pass
        except ConnectionError:
            time.sleep(5)
        except Exception as err:
            logger.exception('Бот упал с ошибкой')
            time.sleep(1)
            """бот продолжает работать (пытаться запускаться), но телеграм отваливается по 
            таймауту на отправке бесконечных сообщений с одной и той же ошибкой, введена пауза"""


if __name__ == "__main__":
    main()

