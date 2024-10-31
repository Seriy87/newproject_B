import ccxt
import pandas as pd
import logging
import time
from config import API_KEY, API_SECRET, SYMBOL, TIMEFRAME, POSITION_SIZE
from strategy import should_place_order, calculate_indicators
from utils import send_telegram_message, calculate_take_profit_and_stop_loss, format_balance_message

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
    """Получение баланса в USDT и WLKN."""
    balance = exchange.fetch_balance()
    usdt_balance = balance['total'].get('USDT', 0)
    wlkn_balance = balance['total'].get('WLKN', 0)
    return usdt_balance, wlkn_balance

def place_order(side, amount):
    """Размещение ордера на бирже и отправка результата в Telegram."""
    try:
        order = exchange.create_market_order(SYMBOL, side, amount)
        send_telegram_message(f"Ордер на {side.upper()} {amount} {SYMBOL} размещен.")
        logging.info(f"Ордер на {side.upper()} {amount} {SYMBOL} размещен.")
        
        # Получение баланса после сделки
        usdt_balance, wlkn_balance = get_balance()
        balance_message = format_balance_message(usdt_balance, wlkn_balance)
        send_telegram_message(f"Результат ордера: {side.upper()} {amount} {SYMBOL}.\n{balance_message}")
        
        return order
    except Exception as e:
        logging.error(f"Ошибка размещения ордера: {e}")
        send_telegram_message(f"Ошибка размещения ордера: {e}")
        return None

def main():
    side = 'sell'  # Стартовая сторона сделки (чередуется после каждой сделки)

    while True:
        try:
            # Основная логика бота
            logging.info("Старт цикла бота.")
            df = get_ohlcv()
            df = calculate_indicators(df)  # Рассчитываем индикаторы
            logging.info("Получены данные OHLCV и рассчитаны индикаторы.")
            last_price = df['close'].iloc[-1]
            logging.info(f"Текущая цена: {last_price}.")

            # Решение по следующему ордеру
            order_side = should_place_order(df, last_price, side)
            if order_side:
                available_balance = get_balance()[0 if order_side == 'buy' else 1]
                if available_balance >= POSITION_SIZE:
                    order = place_order(order_side, POSITION_SIZE)
                    if order:
                        # Устанавливаем уровни прибыли и убытка
                        take_profit, stop_loss = calculate_take_profit_and_stop_loss(last_price, order_side)
                        logging.info(f"Установлены уровни Take Profit: {take_profit}, Stop Loss: {stop_loss}")
                        send_telegram_message(f"Уровни Take Profit: {take_profit}, Stop Loss: {stop_loss}")
                        side = 'buy' if order_side == 'sell' else 'sell'  # Чередование сторон сделки
                    else:
                        logging.info("Не удалось разместить ордер.")
                else:
                    logging.info(f"Недостаточный баланс для ордера. Необходимый: {POSITION_SIZE}, доступный: {available_balance}.")
            time.sleep(1)

        except Exception as e:
            logging.error(f"Ошибка в работе бота: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()
