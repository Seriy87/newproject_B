# Файл конфигурации
# config.py
# Токен бота и ID канала
TOKEN = "7555802784:AAHMOsVjJJlYivpBSdudIgGb1mlqDKdWsSU"  # Замените на токен вашего бота
CHANNEL_ID = "@fireshotnews"  # Замените на имя вашего канала
KEYWORDS = [
    "война", "СВО", "конфликт", "боевые действия", "обстрел", "атака",
    "Украина", "Россия", "Донбасс", "ВСУ", "территории", "территориальная целостность",
    "терроризм", "теракт", "взрыв", "захват", "нападение", "антитеррор",
    "силовые структуры", "МВД", "ФСБ", "Минобороны", "национальная безопасность",
    "чрезвычайное происшествие", "ЧП", "происшествие", "крушение", "катастрофа",
    "авария", "пожар", "взрыв", "трагедия", "жертвы", "гибель",
    "погибшие", "раненые", "эвакуация", "спасение", "спасатели", "спасательные службы",
    "срочные новости", "экстренное сообщение", "неотложные новости", "заявление",
    "обострение", "санкции", "политическое заявление", "конфликтная зона",
    "безопасность", "военное положение", "боеготовность", "мобилизация",
    "израиль", "сектор газа", "ХАМАС", "палестина", "мирные жители",
    "сша", "нато", "запад", "оружие", "вооружение", "боеприпасы",
    "военная техника", "военные действия", "бои", "мирные переговоры", "дезинформация",
    "срочное заявление", "оперативные меры", "захват заложников", "освобождение заложников",
    "разведка", "пограничная безопасность", "военная операция", "боевые потери",
    "контртеррористическая операция", "урегулирование конфликта", "силовые структуры"
]
RSS_FEEDS = [
    "https://www.kommersant.ru/RSS/news.xml",
    "https://tass.ru/rss/v2.xml",
    "https://ria.ru/export/rss2/archive/index.xml",
    "https://lenta.ru/rss",
    "https://www.gazeta.ru/export/rss/lenta.xml",
    "https://rssexport.rbc.ru/rbcnews/news/30/full.rss",
    "https://rg.ru/xml/index.xml",
    "https://www.interfax.ru/rss.asp",
    "https://iz.ru/xml/rss/all.xml",
    "https://www.vedomosti.ru/rss/news"
]
POST_INTERVAL = 10  # секунд
CHECK_INTERVAL = 2100  # 35 минут
WORKING_HOURS = (7, 24)  # с 7:00 до 00:00 по Москве