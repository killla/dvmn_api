import os
import time
import logging

import requests
import telegram
from dotenv import load_dotenv


def parse_messages(server_response):
    messages = server_response['new_attempts']
    for message in messages:
        lesson_title = message['lesson_title']
        lesson_url = message['lesson_url']
        is_negative = message['is_negative']
        send_tg_message(lesson_title, lesson_url, is_negative)


def send_tg_message(title, url, is_negative):
    text = f'У вас проверили работу «{title}»\n{SITE}{url}'
    if is_negative:
        text = text + '\n\nК сожалению, в работе нашлись ошибки.'
    else:
        text = text + '\n\nПреподавателю всё понравилось.'
    BOT.send_message(chat_id=TG_CHAT_ID, text=text)


if __name__ == "__main__":
    load_dotenv()
    LOG_LEVEL = os.getenv("DEBUG")
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    DVMN_TOKEN = os.getenv("DVMN_TOKEN")
    TG_CHAT_ID = os.getenv("TG_CHAT_ID")
    SITE = 'https://dvmn.org'
    API_URL = 'https://dvmn.org/api/long_polling/'
    BOT = telegram.Bot(token=BOT_TOKEN)

    logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s %(levelname)s %(message)s")

    logging.info('bot started')
    payload = {'timestamp_to_request': ''}
    headers = {'Authorization': f'Token {DVMN_TOKEN}'}
    while True:
        try:
            response = requests.get(API_URL, headers=headers, params=payload)
            response.raise_for_status()
            server_response = response.json()
            if server_response['status'] == 'found':
                payload = {'timestamp_to_request': server_response['last_attempt_timestamp']}
                parse_messages(server_response)
            elif server_response['status'] == 'timeout':
                payload = {'timestamp_to_request': server_response['timestamp_to_request']}
        except requests.exceptions.ReadTimeout:
            pass
        except ConnectionError:
            time.sleep(5)
