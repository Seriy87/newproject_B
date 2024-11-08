import requests
from bs4 import BeautifulSoup
import re
import time
from config import SOURCE_URLS
import logging

logger = logging.getLogger(__name__)

url = SOURCE_URLS

def fetch_content(send_all=False):
    # Загружаем страницу
    response = requests.get(url)
    response.raise_for_status()  # Проверяем, что страница загрузилась успешно
    
    # Парсим HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Находим все блоки по шаблону ID для ссылок
    sections = soup.find_all('div', id=re.compile(r'^tiepost-2-section-\d+$'))
    if not sections:
        logger.info("Разделы с указанными ID не найдены.")
        return []

    # Создаем пустое множество для всех уникальных ссылок
    all_links = set()
    
    
    # Проходим по каждому блоку и извлекаем ссылки
    for section in sections:
        for a_tag in section.find_all('a', href=True):
            href = a_tag['href']
            if (not any(href.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.pdf']) and
                not href.startswith('//t.me') and
                not href.startswith('#')):
                all_links.add("https://new-science.ru/"+href)  # Добавляем в множество, автоматически исключая дубли

    # Список для хранения новостей
    news_items = []
    ALL = len(all_links)
    logger.info(f"Собираю статьи их {ALL}. Жди...")

    # Переход по каждой уникальной ссылке
    for link in all_links:
        try:
            article_response = requests.get(link)
            article_response.raise_for_status()
            article_soup = BeautifulSoup(article_response.text, 'html.parser')
            
            # Находим блок с id="content" и классом "site-content container"
            article_main_content = article_soup.find('div', id="content", class_="site-content container")
            if not article_main_content:
                logger.info(f"Основной контент не найден для {link}")
                continue
            
            # Извлекаем изображения и выбираем первое как media_url
            images = [img['src'] for img in article_main_content.find_all('img', src=True)]
            images = ["https://new-science.ru" + img if not img.startswith("http") else img for img in images]
            media_url = images[0] if images else None
            
            # Извлекаем заголовок и текст статьи
            content_text = []
            start_heading = article_main_content.find('h1', class_='post-title entry-title')
            if start_heading:
                title = start_heading.get_text(strip=True).upper()
                content_text.append(title)
                for tag in start_heading.find_all_next(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'em']):
                    if article_main_content.find(tag.name, string=tag.get_text(strip=True)) is None:
                        continue
                    if tag.name == 'em' and "Читайте все последние новости" in tag.get_text(strip=True):
                        break
                    if tag.name in ['h2', 'h3', 'h4', 'h5', 'h6']:
                        content_text.append(f"*{tag.get_text(strip=True)}*")
                    else:
                        content_text.append(tag.get_text(strip=True))

                # Объединяем текст статьи
                content = '\n'.join(content_text)
                news_items.append((title, content, media_url))  # Добавляем статью в виде кортежа
                #logger.info(f"{link}\n {content}")
            else:
                logger.info(f"Заголовок не найден для: {link}")

            time.sleep(1)

        except requests.RequestException as e:
            logger.error(f"Ошибка при загрузке страницы {link}: {e}")

    #logger.info(f"Найдено статей: {len(news_items)}")
    return news_items
