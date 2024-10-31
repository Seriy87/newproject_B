from telegram import Bot
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

# Инициализация бота Telegram
bot = Bot(token=TELEGRAM_TOKEN)

def send_telegram_message(message):
    """Отправка сообщения в Telegram."""
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

def calculate_take_profit_and_stop_loss(last_price, side):
    """Вычисляет уровни Take Profit и Stop Loss."""
    if side == 'sell':
        take_profit = last_price * 0.99  # 1% ниже для Take Profit
        stop_loss = last_price * 1.01  # 1% выше для Stop Loss
    else:
        take_profit = last_price * 1.01  # 1% выше для Take Profit
        stop_loss = last_price * 0.99  # 1% ниже для Stop Loss
    return take_profit, stop_loss
