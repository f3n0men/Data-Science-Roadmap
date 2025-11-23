import requests
import pandas as pd
import matplotlib.pyplot as plt
import time
from datetime import datetime

# примерный курс
EXCHANGE_RATES = {
    'RUR': 1.0,      # Российский рубль
    'RUB': 1.0,      # Российский рубль
    'USD': 80.0
}

def convert_salary_to_rub(salary, currency):

    """Конвертирует зарплату в рубли по курсу"""
    if salary is None or currency is None:
        return None
    
    rate = EXCHANGE_RATES.get(currency)
    if rate is None:
        print(f"Неизвестная валюта: {currency}, зарплата не конвертирована")
        return salary  # Возвращаем как есть, если валюта неизвестна
    
    return salary * rate

def fetch_hh_vacancies(text="data scientist", area=1, per_page=50):
    """
    Получает вакансии с HeadHunter API
    area=1 - Москва, area=2 - СПб
    """
    url = "https://api.hh.ru/vacancies"
    
    params = {
        'text': text,
        'area': area,
        'per_page': per_page,
        'page': 0
    }
    
    all_vacancies = []
    
    try:
        print(f"Ищем вакансии по запросу: '{text}'")
        
        # Делаем запрос к API
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        vacancies = data.get('items', [])
        
        print(f"Найдено вакансий: {data.get('found', 0)}")
        print(f"Загружаем {len(vacancies)} вакансий...")
        
        # Собираем основные данные по вакансиям
        for vacancy in vacancies:
            salary_info = vacancy.get('salary')
            if salary_info is None:
                salary_from = None
                salary_to = None
                currency = None
            else:
                salary_from = salary_info.get('from')
                salary_to = salary_info.get('to')
                currency = salary_info.get('currency')
            
            # Конвертируем зарплаты в рубли
            salary_from_rub = convert_salary_to_rub(salary_from, currency)
            salary_to_rub = convert_salary_to_rub(salary_to, currency)
            
            vacancy_info = {
                'name': vacancy.get('name'),
                'employer': vacancy.get('employer', {}).get('name'),
                'salary_from': salary_from,
                'salary_to': salary_to,
                'salary_from_rub': salary_from_rub,
                'salary_to_rub': salary_to_rub,
                'currency': currency,
                'experience': vacancy.get('experience', {}).get('name'),
                'schedule': vacancy.get('schedule', {}).get('name'),
                'url': vacancy.get('alternate_url')
            }
            all_vacancies.append(vacancy_info)
            
        time.sleep(0.5)
            
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к API: {e}")
        return []
    
    return all_vacancies

def clean_salary_data(df):
    """Очищает данные о зарплатах от выбросов"""

    cleaned_df = df[df['salary_avg_rub'] >= 10000].copy()
    cleaned_df = cleaned_df[cleaned_df['salary_avg_rub'] <= 1000000]
    return cleaned_df

def analyze_vacancies(vacancies):
    """Анализирует собранные вакансии"""

    if not vacancies:
        print("Нет данных для анализа")
        return
    
    df = pd.DataFrame(vacancies)
    print(f"\n=== АНАЛИЗ {len(df)} ВАКАНСИЙ ===")
    
    print("\n1. Первые 5 вакансий:")
    print(df[['name', 'employer', 'salary_from', 'salary_to', 'currency']].head())
    
    print("\n2. Работодатели с наибольшим количеством вакансий:")
    print(df['employer'].value_counts().head(10))
    
    salary_df = df[(df['salary_from_rub'].notna()) | (df['salary_to_rub'].notna())].copy()
    
    if not salary_df.empty:
        # Берем среднюю зарплату в РУБЛЯХ
        salary_df['salary_avg_rub'] = salary_df.apply(
            lambda x: (x['salary_from_rub'] + x['salary_to_rub']) / 2 
            if pd.notna(x['salary_from_rub']) and pd.notna(x['salary_to_rub']) 
            else x['salary_from_rub'] if pd.notna(x['salary_from_rub']) 
            else x['salary_to_rub'], 
            axis=1
        )
        
        print(f"\n3. Распределение по валютам:")
        print(salary_df['currency'].value_counts())
        
        salary_df = clean_salary_data(salary_df)
        
        if not salary_df.empty:
            print(f"\n4. Зарплаты В РУБЛЯХ (анализ {len(salary_df)} вакансий):")
            print(f"   Средняя зарплата: {salary_df['salary_avg_rub'].mean():,.0f} руб.")
            print(f"   Медианная зарплата: {salary_df['salary_avg_rub'].median():,.0f} руб.")
            print(f"   Диапазон: {salary_df['salary_avg_rub'].min():,.0f} - {salary_df['salary_avg_rub'].max():,.0f} руб.")
            
            print(f"\n5. Зарплаты по опыту работы:")
            exp_salary = salary_df.groupby('experience')['salary_avg_rub'].agg(['mean', 'count', 'min', 'max']).round(0)
            print(exp_salary)

            plt.figure(figsize=(15, 5))
            
            plt.subplot(1, 3, 1)
            salary_df['salary_avg_rub'].hist(bins=20, alpha=0.7, color='skyblue')
            plt.title('Распределение зарплат (рубли)')
            plt.xlabel('Зарплата (руб)')
            plt.ylabel('Количество вакансий')
            
            plt.subplot(1, 3, 2)
            df['experience'].value_counts().plot(kind='bar', alpha=0.7, color='lightgreen')
            plt.title('Требуемый опыт работы')
            plt.xticks(rotation=45)
            
            plt.subplot(1, 3, 3)
            salary_df['currency'].value_counts().plot(kind='pie', autopct='%1.1f%%')
            plt.title('Распределение по валютам')
            
            plt.tight_layout()
            plt.savefig('salary_analysis.png')
            print("\nГрафики сохранены как 'salary_analysis.png'")
    
    return df

if __name__ == "__main__":
    print(f"Дата анализа: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    # Ищем вакансии Data Scientist в Москве
    vacancies = fetch_hh_vacancies(text="data scientist", area=1, per_page=100)
    
    if vacancies:
        df = analyze_vacancies(vacancies)
        
        df.to_csv('hh_vacancies.csv', index=False, encoding='utf-8')
        print(f"\nДанные сохранены в файл: hh_vacancies.csv")
        print(f"Всего обработано вакансий: {len(df)}")
    else:
        print("Не удалось получить данные с HH API")