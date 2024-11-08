import os
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID')
SOURCE_URLS = os.getenv('SOURCE_URL').split(",")  # Преобразуем в список URL
NEWS_CHECK_INTERVAL = int(os.getenv('NEWS_CHECK_INTERVAL', 60))  # Интервал проверки новостей в минутах
TOKEN_GEMENI = os.getenv('TOKEN_API_GEMENI')