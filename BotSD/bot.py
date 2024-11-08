import logging
from scheduler import start_scheduler
from database import create_table
from sender import send_news  # Эта строка должна остаться

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    try:
        # Создаем таблицу, если она не существует
        create_table() 
        logger.info("Таблица для отправленных новостей создана или уже существует.")

        # Отправляем все новости при старте
        send_news(send_all=True)
        logger.info("Начальная отправка всех новостей выполнена.")

        # Настраиваем и запускаем планировщик
        scheduler = start_scheduler()
        scheduler.start()
    except Exception as e:
        logger.error(f"Ошибка в работе бота: {e}")
    finally:
        logger.info("Бот остановлен.")

if __name__ == "__main__":
    main()