import os
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID')
SOURCE_URLS = os.getenv('SOURCE_URL')
NEWS_CHECK_INTERVAL = int(os.getenv('NEWS_CHECK_INTERVAL', 60))  # Интервал проверки новостей в минутах
TOKEN_GEMENI = os.getenv('TOKEN_API_GEMENI')
TOKEN_VK = os.getenv('ACCESS_TOKEN_VK')
GROUP_VK = os.getenv('GROUP_ID_VK')
USER_VK = os.getenv('USER_TOKEN_VK')