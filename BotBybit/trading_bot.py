import ccxt
import pandas as pd
import logging
import time
import asyncio
from telegram import Bot
from config import API_KEY, API_SECRET, SYMBOL, TIMEFRAME, POSITION_SIZE, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Подключаемся к бирже
exchange = ccxt.bybit({
    'apiKey': API_KEY,
    'secret': API_SECRET,
    'enableRateLimit': True,
})

# Инициализация бота Telegram
bot = Bot(token=TELEGRAM_TOKEN)

async def send_telegram_message(message):
    """Отправка сообщения в Telegram."""
    try:
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except Exception as e:
        logger.error(f"Не удалось отправить сообщение в Telegram: {e}")

def get_ohlcv():
    """Получаем исторические данные OHLCV."""
    bars = exchange.fetch_ohlcv(SYMBOL, timeframe=TIMEFRAME, limit=50)
    df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    return df

def calculate_levels(df):
    """Расчет уровней для скальпинга."""
    high_level = df['high'].rolling(10).max().iloc[-1]
    low_level = df['low'].rolling(10).min().iloc[-1]
    return high_level, low_level

def get_balance():
    """Получение доступного баланса в USDT."""
    balance = exchange.fetch_balance()
    return balance['total']['USDT']  # Предполагаем, что вы используете USDT

def place_order(side, amount):
    """Размещение ордера на бирже."""
    try:
        order = exchange.create_market_order(SYMBOL, side, amount)
        logger.info(f"Ордер размещен: {side} {amount} {SYMBOL}")
        asyncio.run(send_telegram_message(f"Ордер размещен: {side} {amount} {SYMBOL}"))
        return order
    except Exception as e:
        logger.error(f"Ошибка размещения ордера: {e}")
        asyncio.run(send_telegram_message(f"Ошибка размещения ордера: {e}"))
        return None

def calculate_take_profit_and_stop_loss(last_price, side):
    """Расчет уровней Take Profit и Stop Loss для скальпинга."""
    if side == 'sell':
        take_profit = last_price * 0.995  # 0.5% дохода
        stop_loss = last_price * 1.005  # 0.5% убытка
    else:
        take_profit = last_price * 1.005  # 0.5% дохода
        stop_loss = last_price * 0.995  # 0.5% убытка
    return take_profit, stop_loss

def check_trend(df):
    """Проверка направления тренда с использованием скользящей средней."""
    df['SMA_20'] = df['close'].rolling(window=20).mean()
    return "up" if df['close'].iloc[-1] > df['SMA_20'].iloc[-1] else "down"

# ... (остальной код остается без изменений)

async def main():
    side = 'sell'  # Начинаем с продажи

    while True:
        try:
            logger.info("Старт цикла бота.")
            df = get_ohlcv()
            logger.info("Получены данные OHLCV.")
            high_level, low_level = calculate_levels(df)
            logger.info(f"Уровни для скальпинга: High - {high_level}, Low - {low_level}.")
            last_price = df['close'].iloc[-1]
            logger.info(f"Текущая цена: {last_price}.")

            threshold = 0.000002  # Пониженный порог для активации сигнала
            trend = check_trend(df)
            logger.info(f"Текущий тренд: {trend}")

            # Проверка на пробой уровней с учетом тренда
            order_side = None
            if trend == "up" and side == 'sell' and last_price > (high_level + threshold):
                logger.info("Сигнал на продажу. Размещение ордера...")
                order_side = 'sell'
            elif trend == "down" and side == 'buy' and last_price < (low_level - threshold):
                logger.info("Сигнал на покупку. Размещение ордера...")
                order_side = 'buy'
            else:
                logger.info("Нет сигнала для размещения ордера.")

            if order_side:
                available_balance = get_balance()
                required_amount = POSITION_SIZE

                if available_balance >= required_amount:
                    order = place_order(order_side, required_amount)
                    if order:
                        take_profit, stop_loss = calculate_take_profit_and_stop_loss(last_price, order_side)
                        logger.info(f"Установлены уровни Take Profit: {take_profit}, Stop Loss: {stop_loss}")
                        await send_telegram_message(f"Установлены уровни Take Profit: {take_profit}, Stop Loss: {stop_loss}")
                        side = 'buy' if order_side == 'sell' else 'sell'
                    else:
                        logger.info("Не удалось разместить ордер.")
                else:
                    logger.info(f"Недостаточный баланс. Необходимый: {required_amount}, доступный: {available_balance}. Ордер не будет размещён.")

            await asyncio.sleep(0.5)  # Снижение интервала для более частой проверки

        except Exception as e:
            logger.error(f"Ошибка в работе бота: {e}")
            await send_telegram_message(f"Ошибка в работе бота: {e}")
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
