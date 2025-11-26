
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS  # Добавьте этот импорт
import pandas as pd
import joblib
import json

app = Flask(__name__)
CORS(app)  #
# Загружаем модель и данные
model = joblib.load('apartment_price_predictor.pkl')
with open('station_data.json', 'r', encoding='utf-8') as f:
    station_data = json.load(f)

premium_stations = station_data['premium_stations']
budget_stations = station_data['budget_stations']
features = station_data['features']

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Получаем данные из формы
        data = request.json

        # Подготавливаем признаки для модели
        input_features = {
            'Area': float(data['area']),
            'Number of rooms': float(data['rooms']),
            'Minutes to metro': float(data['minutes_to_metro']),
            'Floor': float(data['floor']),
            'Number of floors': float(data['total_floors']),
            'is_premium_station': 0,
            'is_budget_station': 0
        }

        # Определяем категорию станции метро
        metro_station = data.get('metro_station', '').strip()
        if metro_station:
            if metro_station in premium_stations:
                input_features['is_premium_station'] = 1
            elif metro_station in budget_stations:
                input_features['is_budget_station'] = 1

        # Создаём DataFrame и делаем предсказание
        input_df = pd.DataFrame([input_features], columns=features)
        predicted_price = model.predict(input_df)[0]

        return jsonify({
            'success': True,
            'predicted_price': int(predicted_price),
            'error': None
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'predicted_price': 0,
            'error': str(e)
        })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
