import logging
import requests
import vk_api
from database import mark_news_as_sent, create_table
from config import GROUP_VK, TOKEN_VK, TOKEN_GEMENI

# API Google Gemini
import google.generativeai as genai

genai.configure(api_key=TOKEN_GEMENI)  # Доступ к Google API
model = genai.GenerativeModel('gemini-pro')
command = "Используй научно-популярный стиль и добавь смайл и хэштег"

# Настройки логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Конфигурация
VK_ACCESS_TOKEN = TOKEN_VK
GROUP_ID = GROUP_VK
create_table()


def process_post_text(post_text):
    """Обрабатывает текст поста через Google Gemini."""
    try:
        # Разделяем строку по двойным разделителям
        substrings = post_text.split("\n\n")
        processed_substrings = [
            model.generate_content(command + substring).text for substring in substrings
        ]
        return "\n\n".join(processed_substrings)
    except Exception as e:
        logger.error(f"Ошибка обработки текста через Gemini: {e}")
        return post_text  # Возвращаем исходный текст в случае ошибки


def upload_images(vk_session, group_id, image_urls):
    """Загружает изображения и возвращает список их идентификаторов."""
    upload = vk_api.VkUpload(vk_session)
    attachments = []

    for img_url in image_urls:
        try:
            # Скачиваем изображение
            with requests.get(img_url, stream=True, timeout=10) as img_response:
                img_response.raise_for_status()
                # Загружаем изображение на сервер ВК
                photo = upload.photo_wall(photos=img_response.raw, group_id=group_id)
                attachments.append(f"photo{photo[0]['owner_id']}_{photo[0]['id']}")
        except requests.RequestException as e:
            logger.error(f"Не удалось загрузить изображение {img_url}: {e}")
        except vk_api.exceptions.ApiError as e:
            logger.error(f"Ошибка API VK при загрузке изображения {img_url}: {e}")

    return attachments


def post_to_vk(vk_session, group_id, title, content, images):
    """Публикация поста в группу ВК с текстом и изображениями."""
    try:
        # Загружаем изображения
        attachments = upload_images(vk_session, group_id, images)

        # Обрабатываем текст поста
        processed_content = process_post_text(content)
        post_text = f"{title}\n\n{processed_content}"

        # Публикуем пост
        vk_session.method("wall.post", {
            "owner_id": -int(group_id),  # Отрицательный ID для группы
            "from_group": 1,
            "attachments": ",".join(attachments) if attachments else None,
            "message": post_text
        })

        # Отмечаем новость как отправленную
        mark_news_as_sent(title)
        logger.info(f"Успешно опубликован пост: {title}")

    except vk_api.exceptions.ApiError as e:
        logger.error(f"Ошибка API при публикации поста: {e}")
    except Exception as e:
        logger.error(f"Непредвиденная ошибка при публикации поста: {e}")