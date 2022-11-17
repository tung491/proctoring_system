import os

import cv2
import dataclasses
import requests
from dotenv import load_dotenv

load_dotenv()


@dataclasses.dataclass
class Secrets:
    TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")


def send_message_to_telegram(candidate_name, image):
    ok = cv2.imwrite('candidate.jpg', image)
    with open('candidate.jpg', 'rb') as f:
        data = f.read()
    api_url = f"https://api.telegram.org/bot{Secrets.TELEGRAM_BOT_TOKEN}/sendMessage"
    if candidate_name == 'Candidate':
        candidate_name = "Unknown"
    try:
        response = requests.post(
                api_url, data={
                    "chat_id": Secrets.TELEGRAM_CHAT_ID,
                    "text": f"Hey, Candidate {candidate_name} has suspicious behavior!"
                }
        )
        response = requests.post(
                f"https://api.telegram.org/bot{Secrets.TELEGRAM_BOT_TOKEN}/sendPhoto",
                data={
                    "chat_id": Secrets.TELEGRAM_CHAT_ID,
                }, files={
                    "photo": data
                }
        )
    except Exception as e:
        print(e)
