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

def get_balance(asset='USDT'):
    """Получение доступного баланса актива."""
    balance = exchange.fetch_balance()
    return balance['total'].get(asset, 0)  # Получаем баланс указанного актива

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
    side = 'sell'  # Установка первой сделки на продажу
    first_trade_done = False  # Флаг для контроля первой сделки

    while True:
        try:
            # Проверка и выполнение первой продажи
            if not first_trade_done:
                wlkn_balance = get_balance(asset='WLKN')  # Проверяем баланс WLKN

                if wlkn_balance >= POSITION_SIZE:
                    logging.info("Выполнение первой продажи для старта стратегии.")
                    order = place_order('sell', POSITION_SIZE)
                    if order:
                        first_trade_done = True
                        send_telegram_message("Начальная продажа выполнена.")
                        side = 'buy'  # Следующая сделка будет покупкой
                    else:
                        logging.info("Не удалось выполнить начальную продажу.")
                        time.sleep(5)
                    continue  # Переход к следующему циклу, если первая продажа еще не выполнена

            # Основная логика бота после первой сделки
            logging.info("Старт цикла бота.")
            df = get_ohlcv()
            df = calculate_indicators(df)  # Рассчитываем индикаторы
            logging.info("Получены данные OHLCV и рассчитаны индикаторы.")
            last_price = df['close'].iloc[-1]
            logging.info(f"Текущая цена: {last_price}.")

            # Решение по следующему ордеру
            order_side = should_place_order(df, last_price, side)
            if order_side:
                available_balance = get_balance('USDT' if order_side == 'buy' else 'WLKN')
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
