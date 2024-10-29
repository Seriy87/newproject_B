def calculate_levels(df):
    """Расчет уровней сопротивления и поддержки."""
    high_level = df['high'].max()
    low_level = df['low'].min()
    return high_level, low_level

def check_breakout(last_price, high_level, low_level):
    """Проверяем пробой уровня."""
    if last_price > high_level:
        return 'sell'
    elif last_price < low_level:
        return 'buy'
    return None

def calculate_take_profit_and_stop_loss(price, side):
    """Расчет уровней тейк-профита и стоп-лосса."""
    if side == 'buy':
        take_profit = price * 1.05  # 5% прибыли
        stop_loss = price * 0.95     # 5% убытка
    else:
        take_profit = price * 0.95    # 5% прибыли (для продажи)
        stop_loss = price * 1.05      # 5% убытка (для продажи)
    return take_profit, stop_loss
