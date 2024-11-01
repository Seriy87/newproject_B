import logging
import ccxt
from config import SYMBOL

def place_limit_order(exchange, symbol, side, amount, price):
    """Размещение лимитного ордера."""
    try:
        order = exchange.create_limit_order(symbol, side, amount, price)
        return order
    except Exception as e:
        logging.error(f"Ошибка размещения лимитного ордера: {e}")
        return None

def cancel_order(exchange, order_id):
    """Отмена ордера по ID."""
    try:
        exchange.cancel_order(order_id, SYMBOL)
    except Exception as e:
        logging.error(f"Ошибка отмены ордера: {e}")

def get_balance(exchange, currency):
    balance = exchange.fetch_balance()
    return balance['total'].get(currency, 0)

def calculate_levels(df):
    """Расчет уровней для лимитных ордеров."""
    high_level = df['high'].max()
    low_level = df['low'].min()
    return high_level, low_level
