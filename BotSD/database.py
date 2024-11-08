import sqlite3

# Подключение к базе данных
def get_db_connection():
    conn = sqlite3.connect('news_sent.db')
    return conn

# Создание таблицы для хранения отправленных новостей
def create_table():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sent_news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL UNIQUE
            )
        ''')
        conn.commit()

# Проверка, была ли новость отправлена (используется в send_news)
def is_news_sent(title: str) -> bool:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM sent_news WHERE title = ?", (title,))
        return cursor.fetchone() is not None

# Отметка, что новость была отправлена (используется в send_news)
def mark_news_as_sent(title: str) -> None:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO sent_news (title) VALUES (?)", (title,))
            conn.commit()
        except sqlite3.IntegrityError:
            # Обработка случая, если новость уже существует в базе
            pass