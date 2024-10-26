import feedparser
from config import RSS_FEEDS, KEYWORDS

def fetch_latest_news():
    news_by_source = {}
    
    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            if feed.bozo:  # Проверка на ошибки парсинга
                print(f"Ошибка парсинга RSS-канала {url}: {feed.bozo_exception}")
                continue
            
            news_list = []
            
            for entry in feed.entries:
                title = entry.title
                summary = getattr(entry, "summary", "")  # Задаём пустую строку, если 'summary' отсутствует
                link = entry.link
                media = entry.media_content[0]["url"] if "media_content" in entry else None
                
                # Фильтрация по ключевым словам
                if any(keyword in title.upper() or keyword in summary.upper() for keyword in KEYWORDS):
                    published_time = entry.published_parsed if 'published_parsed' in entry else None
                    news_list.append({
                        "title": title,
                        "summary": summary[:300] + '...',  # Ограничиваем длину аннотации
                        "link": link,
                        "media": media,
                        "published_time": published_time,
                    })
            
            # Сохраняем только последнюю новость из источника
            if news_list:
                # Сортируем по времени публикации в порядке возрастания
                latest_news = sorted(news_list, key=lambda x: x["published_time"], reverse=True)[0]
                news_by_source[url] = latest_news  # Сохраняем только последнюю новость

        except Exception as e:
            print(f"Ошибка при обработке RSS-канала {url}: {e}")
    
    return news_by_source