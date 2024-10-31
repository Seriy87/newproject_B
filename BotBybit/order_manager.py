# order_manager.py

import logging
from config import POSITION_SIZE, TAKE_PROFIT_RATIO, STOP_LOSS_RATIO
from data_fetcher import exchange, SYMBOL

def place_order(side, amount):
    """Размещение ордера на покупку или продажу."""
    try:
        order = exchange.create_market_order(SYMBOL, side, amount)
        logging.info(f"Успешно размещён ордер: {side}, Количество: {amount}, Цена: {order['price']}")
        return order
    except Exception as e:
        logging.error(f"Ошибка размещения ордера: {e}")
        return None

def calculate_take_profit_and_stop_loss(price, side):
    """Расчет уровней тейк-профита и стоп-лосса."""
    if side == 'buy':
        take_profit = price * TAKE_PROFIT_RATIO
        stop_loss = price * STOP_LOSS_RATIO
    else:
        take_profit = price * STOP_LOSS_RATIO
        stop_loss = price * TAKE_PROFIT_RATIO
    return take_profit, stop_loss
