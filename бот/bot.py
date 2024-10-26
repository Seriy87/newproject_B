# bot.py
import time
from datetime import datetime
import telebot
from news_parser import fetch_latest_news
from config import TOKEN, CHANNEL_ID, POST_INTERVAL, CHECK_INTERVAL, WORKING_HOURS

bot = telebot.TeleBot(TOKEN)

# Словарь для отслеживания последней отправленной новости для каждого источника
last_sent_news = {}

def send_news():
    news_items = fetch_latest_news()
    
    # Проходим по каждому источнику и выбираем самую свежую новость
    for source_url, news_list in news_items.items():
        if not news_list:
            continue  # Пропускаем, если нет новостей из источника

        # Находим самую новую новость из источника
        latest_news = news_list[0]
        news_id = latest_news["title"] + latest_news["link"]

        # Проверка, отправляли ли эту новость
        if last_sent_news.get(source_url) == news_id:
            continue  # Если новость уже отправлена, пропускаем источник

        title = latest_news["title"]
        summary = latest_news["summary"]
        link = latest_news["link"]
        message = (
            f"📰 *{title}*\n\n"
            f"{summary}\n\n"
            f"[Читать далее]({link})\n"
            "— — — — — — — — — — — — — — — —\n"
        )
        media = latest_news["media"]

        # Отправляем сообщение с медиа (если есть) или только текст
        try:
            if media:
                if media.endswith(".mp4"):
                    bot.send_video(CHANNEL_ID, media, caption=message, parse_mode="Markdown")
                else:
                    bot.send_photo(CHANNEL_ID, media, caption=message, parse_mode="Markdown")
            else:
                bot.send_message(CHANNEL_ID, message, parse_mode="Markdown")

            # Обновляем запись последней отправленной новости для источника
            last_sent_news[source_url] = news_id

            # Задержка между отправками
            time.sleep(POST_INTERVAL)
        except Exception as e:
            print(f"Ошибка при отправке: {e}")

# Основной цикл работы
if __name__ == "__main__":
    while True:
        current_time = datetime.now().hour
        if WORKING_HOURS[0] <= current_time < WORKING_HOURS[1]:
            send_news()
        time.sleep(CHECK_INTERVAL)
