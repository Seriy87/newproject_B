import logging
from telegram import Bot
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

# Инициализация бота Telegram
bot = Bot(token=TELEGRAM_TOKEN)

def send_telegram_message(message):
    """Отправка сообщения в Telegram."""
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

def calculate_take_profit_and_stop_loss(last_price, side):
    """Расчет уровней Take Profit и Stop Loss."""
    if side == 'sell':
        take_profit = last_price * 1.03  # 3% прибыли
        stop_loss = last_price * 0.98  # 2% убытка
    else:
        take_profit = last_price * 0.98  # 2% убытка
        stop_loss = last_price * 1.03  # 3% прибыли
    return take_profit, stop_loss
