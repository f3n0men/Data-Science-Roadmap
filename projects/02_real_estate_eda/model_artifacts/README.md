#  Moscow Apartment Price Predictor

ML модель для предсказания цен на недвижимость в Москве с точностью 87.1%.

##  Результаты
- **R² Score**: 0.871
- **MAE**: 6,998,662 руб

##  Особенности модели
- Учитывает площадь, комнаты, удаленность от метро, этажность
- Автоматически определяет престижность района по станции метро
- Обучена на 22,558 реальных объявлениях
- Оптимизирована с помощью Random Forest

## Использование

```python
from prediction_function import predict_apartment_price

price = predict_apartment_price(
    area=60,
    rooms=2, 
    minutes_to_metro=10,
    floor=5,
    total_floors=16,
    metro_station='Красногвардейская'
)

print(f"Предсказанная цена: {price:,.0f} руб")
