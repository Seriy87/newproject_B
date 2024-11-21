import time
import random
import schedule
import logging
from fetcher3 import fetch_content
from post_to_vk import post_to_vk
import vk_api
from config import GROUP_VK, TOKEN_VK, NEWS_CHECK_INTERVAL


# Настройки логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Конфигурация
VK_ACCESS_TOKEN = TOKEN_VK
GROUP_ID = GROUP_VK

def publish_news(vk_session):
    """Публикация всех доступных новостей с задержкой между постами."""
    news_items = fetch_content()  # Функция сама собирает только новые новости
    logger.info(f"Найдено {len(news_items)} новых новостей.")

    if not news_items:
        logger.info("Нет новых новостей для публикации.")
        return

    for title, content, images in news_items:
        try:
            # Публикация новости
            post_to_vk(vk_session, GROUP_ID, title, content, images)

            # Случайная задержка перед следующей публикацией
            delay = random.randint(10, 15)
            logger.info(f"Публикация завершена. Следующий пост через {delay} минут.")
            time.sleep(delay * 60)
        except Exception as e:
            logger.error(f"Ошибка при публикации: {e}")
            continue

def scheduled_task(vk_session):
    """Запускается по расписанию для публикации новостей."""
    logger.info("Запуск плановой задачи.")
    publish_news(vk_session)
    logger.info("Плановая задача завершена.")

def main():
    """Главный планировщик."""
    vk_session = vk_api.VkApi(token=VK_ACCESS_TOKEN)

    # Сразу публикуем новости при запуске
    logger.info("Запуск приложения. Сразу публикуем новости.")
    publish_news(vk_session)

    # Настраиваем планировщик: запуск раз в час
    schedule.every(NEWS_CHECK_INTERVAL).minutes.do(scheduled_task, vk_session)

    logger.info("Планировщик запущен. Ожидаем задачи...")

    while True:
        schedule.run_pending()
        time.sleep(NEWS_CHECK_INTERVAL)

if __name__ == "__main__":
    main()