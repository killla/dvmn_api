import os, time
import requests, telegram
from pprint import pprint
from dotenv import load_dotenv


load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
DVMN_TOKEN = os.getenv("DVMN_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")
site = 'https://dvmn.org/'
url = 'https://dvmn.org/api/long_polling/'
headers = {'Authorization':f'Token {DVMN_TOKEN}'}
payload = {'timestamp_to_request':''}
bot = telegram.Bot(token=BOT_TOKEN)


def ParseMessages(response):
    messages = response.json()['new_attempts']
    for message in messages:
        lesson_title = message['lesson_title']
        lesson_url = message['lesson_url']
        is_negative = message['is_negative']
        SendTgMessage(lesson_title, lesson_url, is_negative)


def SendTgMessage(title, url, is_negative):
    text = f'У вас проверили работу «{title}»\n{site}{url}'
    if is_negative:
        text = text + '\n\nК сожалению, в работе нашлись ошибки.'
    else:
        text = text + '\n\nПреподавателю всё понравилось.'
    bot.send_message(chat_id=TG_CHAT_ID, text=text)
    pass


while True:
    try:
        response = requests.get(url, headers=headers, params=payload)
        response.raise_for_status()
        if response.json()['status'] == 'found':
            payload = {'timestamp_to_request': response.json()['last_attempt_timestamp']}
            ParseMessages(response)
        elif response.json()['status'] == 'timeout':
            payload = {'timestamp_to_request': response.json()['timestamp_to_request']}
    except requests.exceptions.HTTPError as error:
        exit("Can't get data from server:\n{0}".format(error))
    except requests.exceptions.ReadTimeout as error:
        time.sleep(5)
    except ConnectionError:
        time.sleep(5)



