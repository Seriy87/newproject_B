import requests
from bs4 import BeautifulSoup
import logging
from database import is_news_sent
from config import SOURCE_URLS

logger = logging.getLogger(__name__)

def fetch_content(send_all=False) -> list:
    all_news = []
    for url in SOURCE_URLS:
        url = url.strip()
        if not url.startswith("http"):
            logger.error(f"Неправильный URL: {url}")
            continue

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'lxml')

            # Находим все заголовки новостей
            news_items = soup.find_all('h3', class_='wp-block-heading')

            for title_tag in news_items:
                title_text = title_tag.text.strip() if title_tag else None
                if not title_text:
                    logger.warning(f"Не найден заголовок для элемента на странице: {url}")
                    continue

                # Пропуск уже отправленных новостей, если send_all=False
                if not send_all and is_news_sent(title_text):
                    logger.info(f"Новость '{title_text}' уже была отправлена.")
                    continue

                # Извлечение текста новости
                news_text_parts = []
                current_tag = title_tag.find_next_sibling()

                # Ищем содержимое между текущим заголовком и следующим заголовком
                while current_tag and not (current_tag.name == 'h3' and 'wp-block-heading' in current_tag.get('class', [])):
                    if current_tag.name == 'p':
                        news_text_parts.append(current_tag.text.strip())
                    current_tag = current_tag.find_next_sibling()

                # Извлечение изображения (если есть) и видео (если есть) в пределах новостей
                media_url = None
                video_url = None
                current_tag = title_tag.find_next_sibling()  # начинаем с того же тега, где мы начали собирать текст новостей

                while current_tag and not (current_tag.name == 'h3' and 'wp-block-heading' in current_tag.get('class', [])):
                    # Извлечение изображения
                    if current_tag.name == 'figure' and 'wp-block-image' in current_tag.get('class', []):
                        media_url = current_tag.img['src'] if current_tag.img else None
                    # Извлечение видео
                    elif current_tag.name == 'figure' and 'wp-block-embed' in current_tag.get('class', []):
                        if current_tag.iframe and 'youtube.com' in current_tag.iframe['src']:
                            video_url = current_tag.iframe['src']
                    current_tag = current_tag.find_next_sibling()

                # Объединяем все найденные абзацы текста ➡️➖✔️
                news_text = "\n".join([f"➡️ {part}" for part in news_text_parts]) if news_text_parts else "Текст новости отсутствует"

                # Формируем итоговую новость с учетом медиафайла
                formatted_title = f"*{title_text.upper()}*"

                # Добавим "желтый" фон для заголовка с помощью специальных символов
                news_entry = f"✅{formatted_title}\n{news_text}"

                # Добавляем ссылку на видео, если она найдена
                if video_url:
                    #video_url = video_url.replace('embed/', 'watch?v=')  # Форматируем URL для Telegram
                    news_entry += f"\n\nСмотрите видео: [Ссылка на видео]({video_url})"
                    logger.error(f"Ссылка на видос {video_url}")

                all_news.append((title_text, news_entry, media_url))

        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при запросе к {url}: {e}")
        except AttributeError as e:
            logger.error(f"Ошибка обработки данных с {url}: {e}")
        except Exception as e:
            logger.error(f"Непредвиденная ошибка с {url}: {e}")

    return all_news