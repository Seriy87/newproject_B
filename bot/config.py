# Файл конфигурации
# config.py
# Токен бота и ID канала
TOKEN = "7555802784:AAHMOsVjJJlYivpBSdudIgGb1mlqDKdWsSU"  # Замените на токен вашего бота
CHANNEL_ID = "@fireshotnews"  # Замените на имя вашего канала
KEYWORDS = ["ВОЙНА", "СВО", "УКРАИНА", "ИЗРАИЛЬ", "ХАМАС", "США", "РОССИЯ", "ВСУ", "МО РФ", "ПУТИН"]
RSS_FEEDS = [
    "https://www.kommersant.ru/RSS/news.xml",
    "https://tass.ru/rss/v2.xml",
    "https://lenta.ru/rss",
    "http://vz.ru/rss.xml",
    "http://russian.rt.com/rss/",
    "http://www.vsesmi.ru/rss/19/",
    "http://www.ras.ru/news/newslist/RssFeeder.aspx?Name=press",
    "http://news2.ru/rss.php?order=new"
]
POST_INTERVAL = 10  # секунд
CHECK_INTERVAL = 2100  # 35 минут
WORKING_HOURS = (7, 24)  # с 7:00 до 00:00 по Москве
