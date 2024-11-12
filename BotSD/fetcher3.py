import requests
from bs4 import BeautifulSoup
from database import is_news_sent
import re
import time
from config import SOURCE_URLS
import logging

logger = logging.getLogger(__name__)

url = SOURCE_URLS

def fetch_content(send_all=False):
    # Загружаем страницу
    response = requests.get(url)
    response.raise_for_status()
    
    # Парсим HTML
    soup = BeautifulSoup(response.text, 'html.parser')
        
    # Находим все блоки по шаблону ID для ссылок
    sections = soup.find_all('div', id=re.compile(r'^tiepost-2-section-\d+$'))
    if not sections:
        logger.info("Разделы с указанными ID не найдены.")
        return []

    # Создаем пустое множество для всех уникальных ссылок
    all_links = set()
    
    # Извлекаем ссылки из блоков
    for section in sections:
        for a_tag in section.find_all('a', href=True):
            href = a_tag['href']
            if not any(href.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.pdf']) and \
               not href.startswith('//t.me') and not href.startswith('#'):
                all_links.add("https://new-science.ru/" + href)

    news_items = []
    ALL = len(all_links)
    logger.info(f"Собираю статьи из {ALL}. Жди...")

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

            # Список для всех изображений и уникальное множество для фильтрации
            images = []
            unique_images = set()

            # Добавляем первое изображение вне зависимости от его имени и формата
            first_img = article_main_content.find('img', src=True)
            if first_img:
                img_url = first_img['src']
                img_url = "https://new-science.ru" + img_url if not img_url.startswith("http") else img_url
                images.append(img_url)
                unique_images.add(img_url)

            # Добавляем остальные изображения, подходящие по шаблону
            image_pattern = re.compile(r'\d+-(?:[a-zA-Z]+|\d+)\.(jpg|jpeg|png|gif|svg)$')  # Регулярное выражение для поиска нужных файлов
            for img_tag in article_main_content.find_all('img', src=True):
                img_url = img_tag['src']
                img_url = "https://new-science.ru" + img_url if not img_url.startswith("http") else img_url
                if img_url not in unique_images and image_pattern.search(img_url):
                    # Проверяем доступность изображения
                    if requests.head(img_url).status_code == 200:
                        images.append(img_url)
                        unique_images.add(img_url)

            # Извлекаем заголовок и текст статьи
            content_text = []
            start_heading = article_main_content.find('h1', class_='post-title entry-title')
            if start_heading:
                title = start_heading.get_text(strip=True).upper()
                content_text.append(title)
                for tag in start_heading.find_all_next(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p']):
                    if article_main_content.find(tag.name, string=tag.get_text(strip=True)) is None:
                        continue
                    if tag.name in ['h2', 'h3', 'h4', 'h5', 'h6']:
                        content_text.append(f"*{tag.get_text(strip=True)}*")
                    else:
                        content_text.append(tag.get_text(strip=True))

                # Объединяем текст статьи
                content = '\n'.join(content_text)
                if is_news_sent(title):
                    logger.info(f"Новость '{title}' уже отправлена, пропускаем.")
                else:
                    news_items.append((title, content, images)) # Добавляем статью с картинками и видео
            else:
                logger.info(f"Заголовок не найден для: {link}")

            time.sleep(1)

        except requests.RequestException as e:
            logger.error(f"Ошибка при загрузке страницы {link}: {e}")

    return news_items