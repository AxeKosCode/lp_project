import requests
from flask import current_app

# key = c3542bda5c9e45749bf122243202803
def weather_by_city(city_name):
    weather_url = current_app.config['WEATHER_URL']
    params = {
        'key': current_app.config['WEATHER_API_KEY'],
        'q': city_name,
        'format': 'json',
        'num_of_days': 2,
        'lang': 'ru'
    }
    try:
        result = requests.get(weather_url, params=params)
        result.raise_for_status()
        weather = result.json()
    except (requests.RequestException, ValueError):
        print('Сетевая ошибка')
        return False
    weather_on_two_days = {}

    # if 'data' in weather:
    #     if 'current_condition' in weather['data']:
    #         try:
    #             return weather['data']['current_condition'][0]
    #         except (IndexError, TypeError):
    #             return False
    # return False

    if 'data' in weather:
        if 'current_condition' in weather['data']:
            try:
                weather_on_two_days['today'] = weather['data']['current_condition'][0]
            except (IndexError, TypeError):
                print('Ошибка получения пакета current_condition')
        if 'weather' in weather['data']:
            try:
                w = weather['data']['weather'][1]
                weather_on_two_days['tomorrow'] = {'date': w['date'], 'tempC': w['avgtempC']}
            except (IndexError, TypeError):
                print('Ошибка получения пакета о прогнозе на завтра')
    return weather_on_two_days

# if __name__ == "__main__":
#     print()
