import requests
import logging
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

def send_telegram_message(message):
    """Функция для отправки сообщений в Telegram."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
    }
    try:
        response = requests.post(url, data=payload)
        if response.status_code != 200:
            logging.error(f"Ошибка при отправке сообщения в Telegram: {response.text}")
    except Exception as e:
        logging.error(f"Не удалось отправить сообщение в Telegram: {e}")
