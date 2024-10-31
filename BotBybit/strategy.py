def calculate_indicators(df):
    """Добавляем индикаторы для анализа."""
    df['high_level'] = df['high'].rolling(window=20).max()
    df['low_level'] = df['low'].rolling(window=20).min()
    return df

def should_place_order(df, last_price, side):
    """Определяет, нужно ли размещать ордер."""
    high_level = df['high_level'].iloc[-1]
    low_level = df['low_level'].iloc[-1]

    if side == 'sell' and last_price >= high_level:
        return 'sell'
    elif side == 'buy' and last_price <= low_level:
        return 'buy'
    return None
