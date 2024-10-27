import feedparser
from config import RSS_FEEDS, KEYWORDS, SUMMARY_LIMIT

def fetch_latest_news():
    news_by_source = {}
    
    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            if feed.bozo:
                print(f"Ошибка парсинга RSS-канала {url}: {feed.bozo_exception}")
                continue
            
            news_list = []
            
            for entry in feed.entries:
                title = entry.title
                summary = getattr(entry, "summary", "")
                link = entry.link
                media = entry.media_content[0]["url"] if "media_content" in entry else None
                published_time = entry.published_parsed if 'published_parsed' in entry else None
                
                # Фильтрация по ключевым словам
                if any(keyword in title.upper() or keyword in summary.upper() for keyword in KEYWORDS):
                    news_list.append({
                        "title": title,
                        "summary": summary[:SUMMARY_LIMIT] + '...',  # Ограничиваем длину аннотации
                        "link": link,
                        "media": media,
                        "published_time": published_time,
                    })
            
            if news_list:
                # Оставляем только последнюю новость
                latest_news = sorted(news_list, key=lambda x: x["published_time"], reverse=True)[0]
                news_by_source[url] = latest_news

        except Exception as e:
            print(f"Ошибка при обработке RSS-канала {url}: {e}")
    
    return news_by_source
