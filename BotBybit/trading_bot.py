import ccxt
import pandas as pd
import logging
import time
from config import API_KEY, API_SECRET, SYMBOL, TIMEFRAME, POSITION_SIZE, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
from utils import send_telegram_message
from order_manager import place_limit_order, cancel_order, get_balance, calculate_levels

# Подключение к бирже
exchange = ccxt.bybit({
    'apiKey': API_KEY,
    'secret': API_SECRET,
    'enableRateLimit': True,
})

# Логирование
logging.basicConfig(level=logging.INFO)

def get_open_orders():
    """Получает открытые ордера и формирует сообщение."""
    try:
        open_orders = exchange.fetch_open_orders(SYMBOL)
        if open_orders:
            message = "Текущие открытые ордера:\n"
            for order in open_orders:
                message += f"ID: {order['id']}, Сторона: {order['side']}, Цена: {order['price']}, Количество: {order['amount']}\n"
            return message
        else:
            return "На данный момент нет открытых ордеров."
    except Exception as e:
        logging.error(f"Ошибка получения открытых ордеров: {e}")
        return "Ошибка получения информации об ордерах."

def main():
    sell_order = None
    buy_order = None
    notified_insufficient_balance = False
    notified_sufficient_balance = False

    # Баланс при запуске
    usdt_balance = get_balance(exchange, 'USDT')
    wlkn_balance = get_balance(exchange, 'WLKN')
    open_orders_message = get_open_orders()
    send_telegram_message(
        f"Бот запущен!\nДоступный баланс USDT: {usdt_balance}\n"
        f"Доступный баланс WLKN: {wlkn_balance}\n{open_orders_message}"
    )

    while True:
        try:
            logging.info("Старт цикла бота.")
            df = exchange.fetch_ohlcv(SYMBOL, timeframe=TIMEFRAME, limit=100)
            df = pd.DataFrame(df, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            high_level, low_level = calculate_levels(df)
            last_price = df['close'].iloc[-1]
            
            logging.info(f"Текущая цена: {last_price}")
            logging.info(f"Расчетная цена продажи: {high_level}, расчетная цена покупки: {low_level}")

            # Проверка баланса
            usdt_balance = get_balance(exchange, 'USDT')
            wlkn_balance = get_balance(exchange, 'WLKN')
            logging.info(f"Доступный баланс USDT: {usdt_balance}")
            logging.info(f"Доступный баланс WLKN: {wlkn_balance}")
            required_balance = POSITION_SIZE * last_price

            if usdt_balance < required_balance:
                if not notified_insufficient_balance:
                    message = (f"Недостаточно средств для ордера.\n"
                               f"Текущий баланс USDT: {usdt_balance}\n"
                               f"Необходимо для ордера: {required_balance:.2f} USDT.")
                    logging.warning(message)
                    send_telegram_message(message)
                    notified_insufficient_balance = True
                    notified_sufficient_balance = False
                continue
            else:
                if not notified_sufficient_balance:
                    send_telegram_message("Баланс снова достаточен для размещения ордера.")
                    notified_sufficient_balance = True
                    notified_insufficient_balance = False

            # Лимитный ордер на продажу
            if last_price >= high_level * 0.999 and (sell_order is None or sell_order['price'] != high_level):
                if sell_order:
                    cancel_order(exchange, sell_order['id'])
                    logging.info("Старый ордер на продажу отменен.")
                
                logging.info("Пытаюсь выставить ордер на продажу...")
                sell_order = place_limit_order(exchange, SYMBOL, 'sell', POSITION_SIZE, high_level)
                if sell_order:
                    message = (f"Выставлен лимитный ордер на продажу по цене: {high_level}\n"
                               f"Текущий баланс USDT: {usdt_balance}\nТекущий баланс WLKN: {wlkn_balance}")
                    logging.info(message)
                    send_telegram_message(message)
                else:
                    logging.error("Не удалось разместить ордер на продажу.")

            # Лимитный ордер на покупку
            if last_price <= low_level * 1.001 and (buy_order is None or buy_order['price'] != low_level):
                if buy_order:
                    cancel_order(exchange, buy_order['id'])
                    logging.info("Старый ордер на покупку отменен.")
                
                logging.info("Пытаюсь выставить ордер на покупку...")
                buy_order = place_limit_order(exchange, SYMBOL, 'buy', POSITION_SIZE, low_level)
                if buy_order:
                    message = (f"Выставлен лимитный ордер на покупку по цене: {low_level}\n"
                               f"Текущий баланс USDT: {usdt_balance}\nТекущий баланс WLKN: {wlkn_balance}")
                    logging.info(message)
                    send_telegram_message(message)
                else:
                    logging.error("Не удалось разместить ордер на покупку.")

            time.sleep(5)

        except ccxt.BaseError as e:
            logging.error(f"Ошибка работы с биржей: {e}")
            time.sleep(10)
        except Exception as e:
            logging.error(f"Неизвестная ошибка: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
