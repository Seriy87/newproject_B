from utils import calculate_take_profit_and_stop_loss

def should_place_order(last_price, high_level, low_level, side):
    """Проверка условий для размещения ордера на покупку или продажу."""
    if side == 'sell' and (high_level*1.01 <= last_price >= high_level):
        return 'sell'
    elif side == 'buy' and (low_level*1.01 >= last_price <= low_level):
        return 'buy'
    return None
