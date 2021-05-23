import os
import time
import logging

import requests
import telegram
from dotenv import load_dotenv


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
    log_level = os.getenv("DEBUG")
    bot_token = os.getenv("bot_token")
    dvmn_token = os.getenv("dvmn_token")
    tg_chat_id = os.getenv("tg_chat_id")
    site = 'https://dvmn.org'
    api_url = 'https://dvmn.org/api/long_polling/'
    bot = telegram.Bot(token=bot_token)

    logging.basicConfig(level=log_level, format="%(asctime)s %(levelname)s %(message)s")

    logging.info('bot started')
    payload = {'timestamp_to_request': ''}
    headers = {'Authorization': f'Token {dvmn_token}'}
    while True:
        try:
            response = requests.get(api_url, headers=headers, params=payload)
            response.raise_for_status()
            server_response = response.json()
            if server_response['status'] == 'found':
                payload = {'timestamp_to_request': server_response['last_attempt_timestamp']}
                messages = server_response['new_attempts']
                send_messages(messages, bot, tg_chat_id, site)
            elif server_response['status'] == 'timeout':
                payload = {'timestamp_to_request': server_response['timestamp_to_request']}
        except requests.exceptions.ReadTimeout:
            pass
        except ConnectionError:
            time.sleep(5)


if __name__ == "__main__":
    load_dotenv()
    main()

