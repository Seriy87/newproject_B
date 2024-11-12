import requests
import logging
import random
import time
from database import mark_news_as_sent
from fetcher3 import fetch_content
from config import TOKEN, CHANNEL_ID, TOKEN_GEMENI

import google.generativeai as genai
genai.configure(api_key=TOKEN_GEMENI)
model = genai.GenerativeModel('gemini-1.5-flash')
command = """Сократи максимум до 110 слов. Для отправки статьи в телеграм + 
Выдели название статьи и добавь немного смайлов для лучшего восприятия статьи.  Используй научно-популярный стиль"""

logger = logging.getLogger(__name__)

def send_news(send_all=False):
    logger.info("Запуск отправки новостей...")

    news = fetch_content(send_all)
    if not news:
        logger.info("Нет новых новостей для отправки.")
        return

    logger.info(f"Всего найдено новостей для отправки: {len(news)}")

    for title, content, images in news:# , videos
        try:
            telegram_content = model.generate_content(command + content).text

            # Отправляем контент в зависимости от наличия изображений
            if images:
                # Отправляем как медиа-группу с текстом и ссылкой на видео
                if send_media_group(images, telegram_content):
                    mark_news_as_sent(title)
                    logger.info(f"Новость '{title}' отправлена в канал.")
                else:
                    logger.info(f"Новость '{title}' НЕ отправлена в канал.")
           
            time.sleep(random.randint(5, 10))
            
        except Exception as e:
            logger.error(f"Ошибка при отправке новости '{title}': {e}")

def send_media_group(images, content):
    if not images:
        logger.error("Нет изображений для отправки.")
        return False
    
    media = [{"type": "photo", "media": img} for img in images]
    media[0]["caption"] = content
    media[0]["parse_mode"] = "Markdown"
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendMediaGroup"
    params = {
        "chat_id": CHANNEL_ID,
        "media": media
    }
    response = requests.post(url, json=params)
    try:
        response.raise_for_status()
        logger.info("Группа фото успешно отправлена.")
        return True
    except requests.exceptions.HTTPError as e:
        logger.error(f"Ошибка при отправке группы фото: {e} | Ответ: {response.text}")
        return False