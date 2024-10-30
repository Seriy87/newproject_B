import ccxt
import pandas as pd
import logging
import time
from telegram import Bot
from config import API_KEY, API_SECRET, SYMBOL, TIMEFRAME, POSITION_SIZE, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

# Подключаемся к бирже
exchange = ccxt.bybit({
    'apiKey': API_KEY,
    'secret': API_SECRET,
    'enableRateLimit': True,
})

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Инициализация бота Telegram
bot = Bot(token=TELEGRAM_TOKEN)

def send_telegram_message(message):
    """Отправка сообщения в Telegram."""
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

def get_ohlcv():
    """Получаем исторические данные OHLCV."""
    bars = exchange.fetch_ohlcv(SYMBOL, timeframe=TIMEFRAME, limit=100)
    df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    return df

def calculate_levels(df):
    """Расчет уровней поддержки и сопротивления."""
    high_level = df['high'].max()
    low_level = df['low'].min()
    return high_level, low_level

def get_balance():
    """Получение доступного баланса."""
    balance = exchange.fetch_balance()
    return balance['total']['USDT']  # Предполагаем, что вы используете USDT

def place_order(side, amount):
    """Размещение ордера на бирже."""
    try:
        order = exchange.create_market_order(SYMBOL, side, amount)
        send_telegram_message(f"Ордер размещен: {side} {amount} {SYMBOL}")
        return order
    except Exception as e:
        logging.error(f"Ошибка размещения ордера: {e}")
        return None

def calculate_take_profit_and_stop_loss(last_price, side):
    """Расчет уровней Take Profit и Stop Loss."""
    if side == 'sell':
        take_profit = last_price * 1.01  # 1% прибыли
        stop_loss = last_price * 0.99  # 1% убытка
    else:
        take_profit = last_price * 0.99  # 1% убытка
        stop_loss = last_price * 1.01  # 1% прибыли
    return take_profit, stop_loss

def main():
    side = 'sell'  # Начинаем с продажи

    while True:
        try:
            logging.info("Старт цикла бота.")
            df = get_ohlcv()
            logging.info("Получены данные OHLCV.")
            high_level, low_level = calculate_levels(df)
            logging.info(f"Уровни для скальпинга: High - {high_level}, Low - {low_level}.")
            last_price = df['close'].iloc[-1]
            logging.info(f"Текущая цена: {last_price}.")

            # Проверка на пробой уровней
            order_side = None
            if side == 'sell':
                if last_price >= high_level:  # Условие продажи на уровне High или выше
                    logging.info("Сигнал на продажу. Размещение ордера...")
                    order_side = 'sell'
                else:
                    logging.info("Нет сигнала на продажу.")
            else:  # side == 'buy'
                if last_price <= low_level:  # Условие покупки на уровне Low или ниже
                    logging.info("Сигнал на покупку. Размещение ордера...")
                    order_side = 'buy'
                else:
                    logging.info("Нет сигнала на покупку.")

            if order_side:
                available_balance = get_balance()
                required_amount = POSITION_SIZE  # Используем фиксированный размер позиции

                if available_balance >= required_amount:
                    order = place_order(order_side, required_amount)
                    if order:
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
