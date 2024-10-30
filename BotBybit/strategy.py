import pandas as pd
from utils import calculate_take_profit_and_stop_loss

def calculate_indicators(df):
    """Расчет индикаторов SMA и импульса для стратегического анализа."""
    df['SMA'] = df['close'].rolling(window=5).mean()  # Краткосрочная SMA
    df['Momentum'] = df['close'].diff()  # Импульс: разница между текущей и предыдущей ценой
    return df

def should_place_order(df, last_price, side):
    """
    Новая стратегия: Проверка условий для ордеров, основанная на импульсе и SMA.
    """
    # Получаем последние значения индикаторов
    latest_sma = df['SMA'].iloc[-1]
    latest_momentum = df['Momentum'].iloc[-1]

    # Условия для ордера
    if side == 'sell' and last_price > latest_sma and latest_momentum > 0:
        return 'sell'  # Продаем, если цена выше SMA и наблюдается импульс роста
    elif side == 'buy' and last_price < latest_sma and latest_momentum < 0:
        return 'buy'  # Покупаем, если цена ниже SMA и наблюдается импульс падения
    return None
