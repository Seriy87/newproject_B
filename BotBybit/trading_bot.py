import ccxt
import pandas as pd
import logging
import time
from config import API_KEY, API_SECRET, SYMBOL, TIMEFRAME, POSITION_SIZE
from strategy import should_place_order, calculate_indicators
from utils import send_telegram_message, calculate_take_profit_and_stop_loss

# Подключение к бирже
exchange = ccxt.bybit({
    'apiKey': API_KEY,
    'secret': API_SECRET,
    'enableRateLimit': True,
})

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_ohlcv():
    """Получаем исторические данные OHLCV."""
    bars = exchange.fetch_ohlcv(SYMBOL, timeframe=TIMEFRAME, limit=100)
    df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    return df

def get_balance():
    """Получение доступного баланса."""
    balance = exchange.fetch_balance()
    return balance['total']['USDT']

def place_order(side, amount):
    """Размещение ордера на бирже."""
    try:
        order = exchange.create_market_order(SYMBOL, side, amount)
        send_telegram_message(f"Ордер размещен: {side} {amount} {SYMBOL}")
        return order
    except Exception as e:
        logging.error(f"Ошибка размещения ордера: {e}")
        return None

def main():
    side = 'sell'  # Начинаем с продажи

    while True:
        try:
            logging.info("Старт цикла бота.")
            df = get_ohlcv()
            df = calculate_indicators(df)  # Рассчитываем индикаторы
            logging.info("Получены данные OHLCV и рассчитаны индикаторы.")
            last_price = df['close'].iloc[-1]
            logging.info(f"Текущая цена: {last_price}.")

            order_side = should_place_order(df, last_price, side)
            if order_side:
                available_balance = get_balance()
                required_amount = POSITION_SIZE

                if available_balance >= required_amount:
                    order = place_order(order_side, required_amount)
                    if order:
                        # Устанавливаем более близкие уровни прибыли и убытка
                        take_profit, stop_loss = calculate_take_profit_and_stop_loss(last_price, order_side)
                        logging.info(f"Установлены уровни Take Profit: {take_profit}, Stop Loss: {stop_loss}")
                        send_telegram_message(f"Уровни Take Profit: {take_profit}, Stop Loss: {stop_loss}")
                        side = 'buy' if order_side == 'sell' else 'sell'
                    else:
                        logging.info("Не удалось разместить ордер.")
                else:
                    logging.info(f"Недостаточный баланс. Необходимый: {required_amount}, доступный: {available_balance}. Ордер не будет размещён.")

            time.sleep(1)

        except Exception as e:
            logging.error(f"Ошибка в работе бота: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()
