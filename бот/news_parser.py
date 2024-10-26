# news_parser.py
import feedparser
from config import RSS_FEEDS, KEYWORDS

def fetch_latest_news():
    news_by_source = {}
    
    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        news_list = []
        
        for entry in feed.entries:
            title = entry.title
            summary = getattr(entry, "summary", "")  # Задаём пустую строку, если 'summary' отсутствует
            link = entry.link
            media = entry.media_content[0]["url"] if "media_content" in entry else None
            
            # Фильтрация по ключевым словам
            if any(keyword in title.upper() or keyword in summary.upper() for keyword in KEYWORDS):
                news_list.append({
                    "title": title,
                    "summary": summary[:300] + '...',  # Ограничиваем длину аннотации
                    "link": link,
                    "media": media,
                })
        
        # Сохраняем только одну свежую новость из источника
        if news_list:
            news_by_source[url] = sorted(news_list, key=lambda x: x["link"], reverse=True)
    
    return news_by_source
