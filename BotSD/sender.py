import requests
import logging
import random
import time
from database import is_news_sent, mark_news_as_sent
from fetcher3 import fetch_content  # Импорт функции fetch_content
from config import TOKEN, CHANNEL_ID, TOKEN_GEMENI

logger = logging.getLogger(__name__)

#API Google Gemeni 
import google.generativeai as genai
genai.configure(api_key=TOKEN_GEMENI) #Доступ к гугл апи
model = genai.GenerativeModel('gemini-1.5-flash')
command = """Сократи максимум до 100 слов. Для отправки статьи в телеграм + 
Выдели название статьи и добавь немного смайлов Для лучшего восприятия статьи."""
#response = model.generate_content(input_text)

def send_news(send_all=False):
    logger.info("Запуск отправки новостей...")
    
    news = fetch_content(send_all)  # Передаем флаг в fetch_content
    if not news:
        logger.info("Нет новых новостей для отправки.")
        return  # Прекращаем выполнение, если нет новостей

    logger.info(f"Всего найдено новостей для отправки: {len(news)}")

    for title, content, media_url in news:
        try:
            # Проверяем, была ли новость уже отправлена
            if is_news_sent(title):
                logger.info(f"Новость '{title}' уже отправлена, пропускаем.")
                continue  # Пропускаем эту новость, если она уже была отправлена

            # Отправляем новость с медиа
            
            # Отправляем новость с медиа
            #content = model.generate_content("Сделай сообщение для телеграм"+content)
            #if send_media(content, media_url):  # Здесь отправляем медиа
            #response = model.generate_content(input_text)
            #print(response.text)
            if send_media(model.generate_content(command+content).text, media_url):  # Здесь отправляем медиа
                mark_news_as_sent(title)  # Отмечаем новость как отправленную
                logger.info(f"Новость '{title}' отправлена в канал.")
            else:
                logger.info(f"Новость '{title}' НЕ !!!отправлена в канал.")

            # Пауза перед следующей отправкой
            time.sleep(random.randint(15, 30))  # Пауза перед следующей отправкой
        except Exception as e:
            logger.error(f"Ошибка при отправке новости '{title}': {e}")

def send_media(content, media_url):
    if media_url:
        # Проверяем, является ли медиа URL видео с YouTube
        if "youtube.com" in media_url or "youtu.be" in media_url:
            # Форматируем URL для отправки
            video_url = media_url.replace('embed/', 'watch?v=')
            url = f"https://api.telegram.org/bot{TOKEN}/sendVideo"
            params = {
                "chat_id": CHANNEL_ID,
                "video": video_url,  # Используем форматированную ссылку
                "caption": content,
                "parse_mode": "Markdown"  # Используем Markdown для форматирования
            }
        else:
            url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
            params = {
                "chat_id": CHANNEL_ID,
                "photo": media_url,
                "caption": content,
                "parse_mode": "Markdown"  # Используем Markdown для форматирования
            }

        # Логирование параметров запроса
        #logger.info(f"Отправка медиа с параметрами: {params}")
        
        # Отправка запроса и обработка ответа
        response = requests.post(url, data=params)
        try:
            response.raise_for_status()
            #logger.info("Медиа успешно отправлено.")
        except requests.exceptions.HTTPError as e:
            logger.error(f"Ошибка при отправке медиа: {e} | Ответ: {response.text}")
        return False
    else:
        logger.warning("Медиафайл отсутствует, пропуск отправки.")
        return True