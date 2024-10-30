import logging
from telegram import Bot
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

# ������������� ���� Telegram
bot = Bot(token=TELEGRAM_TOKEN)

def send_telegram_message(message):
    """�������� ��������� � Telegram."""
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

def calculate_take_profit_and_stop_loss(last_price, side):
    """������ ������� Take Profit � Stop Loss."""
    if side == 'sell':
        take_profit = last_price * 1.03  # 1% �������
        stop_loss = last_price * 0.98  # 1% ������
    else:
        take_profit = last_price * 0.97  # 1% ������
        stop_loss = last_price * 1.02  # 1% �������
    return take_profit, stop_loss
