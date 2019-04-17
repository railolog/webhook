import requests
import json

conditions = {
    'clear': 'ясно',
    'partly-cloudy': 'малооблачно',
    'cloudy': 'облачно с прояснениями',
    'overcast': 'пасмурно',
    'partly-cloudy-and-light-rain': 'небольшой дождь',
    'partly-cloudy-and-rain': 'дождь',
    'overcast-and-rain': 'сильный дождь',
    'overcast-thunderstorms-with-rain': 'сильный дождь, гроза',
    'cloudy-and-light-rain': 'небольшой дождь',
    'overcast-and-light-rain': 'небольшой дождь',
    'cloudy-and-rain': 'дождь',
    'overcast-and-wet-snow': 'дождь со снегом',
    'partly-cloudy-and-light-snow': 'небольшой снег',
    'partly-cloudy-and-snow': 'снег',
    'overcast-and-snow': 'снегопад',
    'cloudy-and-light-snow': 'небольшой снег',
    'overcast-and-light-snow': 'небольшой снег',
    'cloudy-and-snow': 'снег'
             }

winds = {
    'nw': 'северо-западный',
    'n': 'северный',
    'ne': 'северо-восточный',
    'e': 'восточный',
    'se': 'юго-восточный',
    's': 'южный',
    'sw': 'юго-западный',
    'w': 'западный',
    'c': 'штиль'
        }


def get_tmr_weather(name='', dict={}):
    try:
        lon, lat = [float(i) for i in dict[name.lower()].split(',')]
    except:
        lon, lat = get_coords(name)
    params = {'lat': lat,
              'lon': lon}

    headers = {'X-Yandex-API-Key': '9d30ba93-d4ac-4638-bac9-f8b35b830bbf'}

    url = 'https://api.weather.yandex.ru/v1/forecast'

    r = requests.get(url, params=params, headers=headers)

    city_name = ''
    for part in name.split():
        city_name += part[0].upper() + part[1:] + ' '
    if '-' in city_name:
        city_name = ''
        for part in name.split('-'):
            city_name += part[0].upper() + part[1:] + '-'

    weather = 'Прогноз погоды на завтра, ' + city_name[:-1] + '.\n'

    json = r.json()
    forecast = json['forecasts'][1]['parts']
    day, night = forecast['day_short'], forecast['night_short']
    weather += 'Днём ' + str(day['temp']) + '°C' + ' и ' + conditions[day['condition']]
    weather += ', а ночью ' + str(night['temp']) + '°C' + ' и ' + conditions[night['condition']]
    return weather


def get_fact_weather(name='', dict={}):
    try:
        lon, lat = [float(i) for i in dict[name.lower()].split(',')]
    except:
        lon, lat = get_coords(name)
    params = {'lat': lat,
              'lon': lon}

    headers = {'X-Yandex-API-Key': '9d30ba93-d4ac-4638-bac9-f8b35b830bbf'}

    url = 'https://api.weather.yandex.ru/v1/forecast'

    r = requests.get(url, params=params, headers=headers)

    city_name = ''
    for part in name.split():
        city_name += part[0].upper() + part[1:] + ' '
    if '-' in city_name:
        city_name = ''
        for part in name.split('-'):
            city_name += part[0].upper() + part[1:] + '-'

    weather = 'Погода ' + city_name[:-1] + '.\n'

    weather = 'Погода ' + city_name.strip() + '.\n'

    json = r.json()
    fact = json['fact']

    condition = conditions[fact['condition']]

    if fact['wind_dir'] == 'c':
        wind = 'штиль'
    else:
        wind = winds[fact['wind_dir']] + ' ветер, со скоростью ' +\
               str(fact['wind_speed']) + ' м/с'

    weather += ', '.join([condition[0].upper() + condition[1:],
                         str(fact['temp']) + '°C',
                         'ощущается как ' + str(fact['feels_like']) + '°C',
                         wind])

    return weather


def get_coords(city_name):
    try:
        url = "https://geocode-maps.yandex.ru/1.x/"
        params = {
            'geocode': city_name,
            'format': 'json'
        }
        response = requests.get(url, params)
        json_r = response.json()
        coordinates_str = json_r['response']['GeoObjectCollection'][
            'featureMember'][0]['GeoObject']['Point']['pos']
        long, lat = coordinates_str.split()
        return long, lat
    except KeyError as e:
        return e


def start_server():
    params = {'lat': 55,
              'lon': 30}

    headers = {'X-Yandex-API-Key': '9d30ba93-d4ac-4638-bac9-f8b35b830bbf'}

    url = 'https://api.weather.yandex.ru/v1/forecast'

    r = requests.get(url, params=params, headers=headers)
