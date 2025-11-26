
def predict_apartment_price(area, rooms, minutes_to_metro, floor, total_floors, metro_station=None):
    """
    Предсказывает цену квартиры в Москве
    """
    import pandas as pd
    import joblib

    # Загружаем модель и данные
    model = joblib.load('apartment_price_predictor.pkl')

    features = {
        'Area': area,
        'Number of rooms': rooms,
        'Minutes to metro': minutes_to_metro,
        'Floor': floor,
        'Number of floors': total_floors,
        'is_premium_station': 0,
        'is_budget_station': 0
    }

    if metro_station in premium_stations:
        features['is_premium_station'] = 1
    elif metro_station in budget_stations:
        features['is_budget_station'] = 1

    input_df = pd.DataFrame([features])
    return model.predict(input_df)[0]
