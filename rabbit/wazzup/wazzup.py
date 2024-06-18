import requests
import re
import os
import uuid

send_url = 'https://api.wazzup24.com/v2/send_message'

channel_id = os.environ.get('CHANNEL_ID','')


def send_message(phone, message):
    p = re.sub("\D", "", phone)
    headers = {"Authorization":"Basic "+os.environ.get('AUTH','')}
    data = {"chatType":"whatsapp","channelId":channel_id,"chatId":p,"text":message}
    resp = requests.post(send_url, data=data, headers=headers)
    print(resp.json())