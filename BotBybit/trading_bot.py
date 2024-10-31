import ccxt
import pandas as pd
import logging
import time
from config import API_KEY, API_SECRET, SYMBOL, TIMEFRAME, POSITION_SIZE
from strategy import calculate_indicators
from utils import send_telegram_message, calculate_take_profit_and_stop_loss, format_balance_message

# Подключение к бирже
exchange = ccxt.bybit({
    'apiKey': API_KEY,
    'secret': API_SECRET,
    'enableRateLimit': True,
})

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Хранение ID открытых ордеров
current_sell_order_id = None
current_buy_order_id = None

def get_ohlcv():
    """Получаем исторические данные OHLCV."""
    bars = exchange.fetch_ohlcv(SYMBOL, timeframe=TIMEFRAME, limit=100)
    df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    return df

def get_balance():
    """Получение баланса в USDT и WLKN."""
    balance = exchange.fetch_balance()
    usdt_balance = balance['total'].get('USDT', 0)
    wlkn_balance = balance['total'].get('WLKN', 0)
    return usdt_balance, wlkn_balance

def cancel_order(order_id):
    """Отмена ордера по ID."""
    try:
        exchange.cancel_order(order_id, SYMBOL)
        logging.info(f"Отложенный ордер {order_id} отменен.")
    except Exception as e:
        logging.error(f"Ошибка отмены ордера {order_id}: {e}")

def place_limit_order(side, amount, price):
    """Размещение лимитного ордера."""
    try:
        order = exchange.create_limit_order(SYMBOL, side, amount, price)
        send_telegram_message(f"Лимитный ордер на {side.upper()} {amount} {SYMBOL} по цене {price} размещен.")
        logging.info(f"Лимитный ордер на {side.upper()} {amount} {SYMBOL} по цене {price} размещен.")
        return order['id']
    except Exception as e:
        logging.error(f"Ошибка размещения лимитного ордера: {e}")
        send_telegram_message(f"Ошибка размещения лимитного ордера: {e}")
        return None

def main():
    global current_sell_order_id, current_buy_order_id
    last_sell_price = None
    last_buy_price = None

    while True:
        try:
            # Основная логика бота
            logging.info("Старт цикла бота.")
            df = get_ohlcv()
            df = calculate_indicators(df)
            logging.info("Получены данные OHLCV и рассчитаны индикаторы.")
            last_price = df['close'].iloc[-1]
            logging.info(f"Текущая цена: {last_price}.")

            # Уровни для расчетных цен покупки и продажи
            high_level = df['high'].max()
            low_level = df['low'].min()
            sell_price = high_level  # Расчетная цена продажи
            buy_price = low_level    # Расчетная цена покупки
            logging.info(f"Расчетная цена продажи: {sell_price}, расчетная цена покупки: {buy_price}.")

            # Обновление ордеров при изменении уровней
            if sell_price != last_sell_price:
                if current_sell_order_id:
                    cancel_order(current_sell_order_id)
                current_sell_order_id = place_limit_order('sell', POSITION_SIZE, sell_price)
                last_sell_price = sell_price

            if buy_price != last_buy_price:
                if current_buy_order_id:
                    cancel_order(current_buy_order_id)
                current_buy_order_id = place_limit_order('buy', POSITION_SIZE, buy_price)
                last_buy_price = buy_price

            # Ожидание перед следующим циклом
            time.sleep(1)

        except Exception as e:
            logging.error(f"Ошибка в работе бота: {e}")
            send_telegram_message(f"Ошибка в работе бота: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()
