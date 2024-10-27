import time
import datetime
import requests
from telebot import TeleBot
from news_parser import fetch_latest_news
from config import TOKEN, CHANNEL_ID, POST_INTERVAL, CHECK_INTERVAL, QUIET_HOURS

bot = TeleBot(TOKEN)

def download_media(media_url):
    try:
        response = requests.get(media_url, stream=True)
        if response.status_code == 200:
            return response.raw
    except Exception as e:
        print(f"Не удалось загрузить медиа: {e}")
    return None

def send_news():
    last_posted = {}

    while True:
        now = datetime.datetime.now()
        # Проверяем время "молчания" (с поправкой на время сервера - швеция)
        if QUIET_HOURS[0] - 3 <= now.hour < QUIET_HOURS[1] - 3:
            time.sleep(1800)
            continue

        # Получаем последние новости
        news_by_source = fetch_latest_news()

        for source, latest_news in news_by_source.items():
            news_id = latest_news["link"]
            published_time = latest_news["published_time"]

            # Проверяем, не было ли отправлено это сообщение
            if last_posted.get(source) == news_id:
                continue

            # Формируем сообщение
            message = f"*{latest_news['title']}*\n\n{latest_news['summary']}\n[Читать далее]({latest_news['link']})"
            
            # Загружаем и отправляем медиа, если доступно
            if latest_news["media"]:
                media_file = download_media(latest_news["media"])
                if media_file:
                    try:
                        bot.send_photo(CHANNEL_ID, media_file, caption=message, parse_mode="Markdown")
                    except Exception as e:
                        print(f"Ошибка при отправке фото: {e}")
                else:
                    try:
                        bot.send_message(CHANNEL_ID, message, parse_mode="Markdown")
                    except Exception as e:
                        print(f"Ошибка при отправке сообщения: {e}")
            else:
                try:
                    bot.send_message(CHANNEL_ID, message, parse_mode="Markdown")
                except Exception as e:
                    print(f"Ошибка при отправке сообщения: {e}")

            # Запоминаем последнюю отправленную новость
            last_posted[source] = news_id

            # Задержка между отправками
            time.sleep(POST_INTERVAL)

        # Ожидание до следующей проверки новостей
        time.sleep(CHECK_INTERVAL)

# Запуск функции отправки новостей
if __name__ == "__main__":
    send_news()
