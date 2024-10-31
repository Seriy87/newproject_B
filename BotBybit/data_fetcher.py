import ccxt
import pandas as pd
import logging
from config import API_KEY, API_SECRET, SYMBOL, TIMEFRAME, LOOKBACK_PERIOD

# Подключаемся к бирже
exchange = ccxt.bybit({
    'apiKey': API_KEY,
    'secret': API_SECRET,
    'enableRateLimit': True,
})

def get_ohlcv():
    """Получаем исторические данные OHLCV."""
    bars = exchange.fetch_ohlcv(SYMBOL, timeframe=TIMEFRAME, limit=LOOKBACK_PERIOD)
    df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    return df

def get_min_order_size():
    """Получаем минимальный размер ордера для торговой пары."""
    market_info = exchange.market(SYMBOL)
    return market_info['limits']['amount']['min']

def get_balance():
    """Получаем доступный баланс."""
    balance = exchange.fetch_balance()
    return balance['total']['USDT']  # Измените на нужный вам валютный счет

def place_order(side, amount):
    """Размещение ордера на покупку или продажу."""
    try:
        order = exchange.create_market_order(SYMBOL, side, amount)
        logging.info(f"Успешно размещён ордер: {side}, Количество: {amount}, Цена: {order['price']}")
        return order
    except Exception as e:
        logging.error(f"Ошибка размещения ордера: {e}")
        return None
