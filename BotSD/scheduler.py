from apscheduler.schedulers.blocking import BlockingScheduler
from sender import send_news
import logging
from config import NEWS_CHECK_INTERVAL

logger = logging.getLogger(__name__)

def start_scheduler():
    logger.info("Запуск планировщика...")
    scheduler = BlockingScheduler()

    # Задаем задачу с интервалом
    scheduler.add_job(send_news_task, 'interval', minutes=NEWS_CHECK_INTERVAL)
    
    try:
        scheduler.start()  # Запуск планировщика
    except (KeyboardInterrupt, SystemExit):
        logger.info("Остановка планировщика...")
        scheduler.shutdown()

def send_news_task():
    try:
        send_news()
        logger.info("Задача send_news выполнена успешно.")
    except Exception as e:
        logger.error(f"Ошибка при выполнении задачи send_news: {e}")