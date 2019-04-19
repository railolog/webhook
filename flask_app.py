from flask import Flask, request
import os
import json
import random
import logging
import datetime
import news_parser
import weather_parser

app = Flask(__name__)
basepath = os.path.abspath(".")

all_names = open(basepath + '/names.txt').read().split()
all_words = open(basepath + '/word_rus.txt').read().split('\n')
ready_coords = json.loads(open(basepath + '/ready_coords.json', 'rb').read())

farewells = ["пока", "до свидания", "до скорой встречи", "прощай",
             "увидимся", "бывай"]

logging.basicConfig(level=logging.INFO)

sessionStorage = {}


@app.route('/post', methods=['POST'])
def main():
    req = request.json
    logging.info('Request: %r', req)
    response = {
        'session': req['session'],
        'version': req['version'],
        'response': {
            'end_session': False
        }
    }
    handle_dialog(response, req)
    logging.info('Response: %r', response)
    try:
        response['response']['buttons'] += [{'title': 'Что ты умеешь?',
                                             'hide': True}]
    except:
        response['response']['buttons'] = [{'title': 'Что ты умеешь?',
                                            'hide': True}]
    return json.dumps(response)


def handle_dialog(res, req):
    user_id = req['session']['user_id']
    if req['session']['new']:
        greeting = get_greeting()
        res['response']['text'] = greeting + '! Назови свое имя!'
        sessionStorage[user_id] = {
            'first_name': None
        }
        sessionStorage[user_id]['playing_words'] = False
        sessionStorage[user_id]['playing_names'] = False
        return

    helps = ['помощь', 'что ты умеешь']
    if any(x in req['request']['original_utterance'].lower() for x in helps):
        res['response']['text'] = 'Чтобы узнать погоду скажи мне ' + \
                                  '"погода в (интересущий тебя город)",' + \
                                  ' чтобы узнать погоду на завтра, добавь ' + \
                                  'слово "завтра".\n' + \
                                  'Для того, чтобы сыграть в слова, напиши' + \
                                  ' "играть в слова", для того, чтобы ' + \
                                  'сыграть в имена, напиши "играть в имена"' + \
                                  ', чтобы узнать новости скажи "новости".'
        return

    if sessionStorage[user_id]['first_name'] is None:
        first_name = get_first_name(req)

        if req['session']['new']:
            res['response']['text'] = 'Привет! Назови свое имя!'
            sessionStorage[user_id] = {
                'first_name': None
            }
            return

        if sessionStorage[user_id]['first_name'] is None:
            first_name = get_first_name(req)

            if first_name is None:
                res['response']['text'] = \
                    'Не расслышала имя. Повтори, пожалуйста!'
            else:
                sessionStorage[user_id]['first_name'] = first_name
                res['response'][
                    'text'] = 'Приятно познакомиться, ' + first_name.title()\
                              + '. Я - Алиса. Ты можешь узнать последние новости \
                              , погоду в своём городе, а также сыграть со мной \
                              в слова или в имена'
                res['response']['buttons'] = [
                    {
                        'title': 'Новости',
                        'hide': True
                    },
                    {
                        'title': 'Как узнать погоду?',
                        'hide': True
                    },
                    {
                        'title': 'Играть в слова',
                        'hide': True
                    },
                    {
                        'title': 'Играть в имена',
                        'hide': True
                    }
                                             ]
            return

    if 'хватит' in req['request']['nlu']['tokens']:
        res['response']['text'] = 'Приятно было поиграть!'
        sessionStorage[user_id]['playing_words'] = False
        sessionStorage[user_id]['playing_names'] = False
        sessionStorage[user_id]['last'] = ''
        sessionStorage[user_id]['used'] = []
        return

    if sessionStorage[user_id]['playing_names']:
        u_name = req['request']['original_utterance'].strip().lower()
        last_lit = sessionStorage[user_id]['last']
        if u_name[0] != last_lit and last_lit != '':
            res['response']['text'] = 'Это имя не подходит :('
        elif u_name in all_names and u_name not in sessionStorage[user_id]['used']:
            last_lit = u_name[-1]
            copy = u_name
            while last_lit in ['ь', 'ъ', 'ы']:
                copy = copy[:-1]
                last_lit = copy[-1]
            filtered_names = list(filter(lambda x: x[0] == last_lit, all_names))
            my_name = random.choice(filtered_names)
            while my_name in sessionStorage[user_id]['used']:
                my_name = random.choice(filtered_names)

            sessionStorage[user_id]['used'].append(u_name)
            sessionStorage[user_id]['used'].append(my_name)
            res['response']['text'] = my_name[0].upper() + my_name[1:]
            while my_name[-1] in ['ь', 'ъ', 'ы']:
                my_name = my_name[:-1]
            sessionStorage[user_id]['last'] = my_name[-1]
        elif u_name not in all_names:
            res['response']['text'] = 'Я не знаю такого имени. Попробуй ещё раз.'
        elif u_name in sessionStorage[user_id]['used']:
            res['response']['text'] = 'Это имя уже говорили. Придумай другое'
        res['response']['buttons'] = [{'title': 'Хватит', 'hide': True}]
        return

    if sessionStorage[user_id]['playing_words']:
        u_word = req['request']['original_utterance'].strip().lower()
        last_lit = sessionStorage[user_id]['last']
        if u_word[0] != last_lit and last_lit != '':
            res['response']['text'] = 'Это слово не подходит :('
        elif u_word in all_words and u_word not in sessionStorage[user_id]['used']:
            last_lit = u_word[-1]
            copy = u_word
            while last_lit in ['ь', 'ъ', 'ы']:
                copy = copy[:-1]
                last_lit = copy[-1]
            filtered_words = list(filter(lambda x: x[0] == last_lit, all_words))
            my_word = random.choice(filtered_words)
            while my_word in sessionStorage[user_id]['used']:
                my_word = random.choice(filtered_words)
            sessionStorage[user_id]['used'].append(u_word)
            sessionStorage[user_id]['used'].append(my_word)
            res['response']['text'] = my_word[0].upper() + my_word[1:]
            while my_word[-1] in ['ь', 'ъ', 'ы']:
                my_word = my_word[:-1]
            sessionStorage[user_id]['last'] = my_word[-1]
        elif u_word not in all_words:
            res['response']['text'] = 'Я не знаю такого слова. Попробуй ещё раз.'
        elif u_word in sessionStorage[user_id]['used']:
            res['response']['text'] = 'Это слово уже говорили. Придумай другое'
        res['response']['buttons'] = [{'title': 'Хватит', 'hide': True}]
        return

    if 'как узнать погоду' in req['request']['original_utterance'].lower():
        res['response']['text'] = 'Скажи мне: погода в (город, о котором\
                                   ты хочешь узнать). Если хочешь узнать \
                                   прогноз на завтра, добавь слово "завтра".'
        return

    variables = ["погода", "погоды", "погоду"]
    if any(x in req['request']['nlu']['tokens'] for x in variables):
        city_name = get_city(req)
        if city_name is None:
            res['response']['text'] = 'Я знаю погоду только в городах.'
            return
        if 'завтра' in req['request']['nlu']['tokens']:
            weather = weather_parser.get_tmr_weather(city_name, ready_coords)
        else:
            weather = weather_parser.get_fact_weather(city_name, ready_coords)
        res['response']['text'] = weather
        return

    if 'новости' in req['request']['nlu']['tokens']:
        news = news_parser.get_news()
        res['response']['text'] = news[0] + '\n' + news[1]
        res['response']['buttons'] = [{'title': 'Открыть на сайте',
                                       'hide': True,
                                       'url': news[2]}]
        return

    if req['request']['original_utterance'] == 'Открыть на сайте':
        res['response']['text'] = 'Новости обновляются с периодичностью 2-4 часа'
        res['response']['buttons'] = [
            {
                'title': 'Новости',
                'hide': True
            },
            {
                'title': 'Как узнать погоду?',
                'hide': True
            }
                                     ]
        return

    if any(x.lower() in req['request']['original_utterance'].lower() for x in farewells):
        res['response']['text'] = 'Пока. Приятно было пообщаться'
        res['response']['end_session'] = True
        return

    if 'в' in req['request']['nlu']['tokens']:
        if 'слова' in req['request']['nlu']['tokens']:
            res['response']['text'] = 'Хорошо. Ты начинаешь. Чтобы \
                                       закончить, скажи "хватит"'

            sessionStorage[user_id]['playing_words'] = True
            sessionStorage[user_id]['last'] = ''
            res['response']['buttons'] = [{'title': 'Хватит', 'hide': True}]
        elif 'имена' in req['request']['nlu']['tokens']:
            res['response']['text'] = 'Давай сыграем. Ты начинаешь. Чтобы \
                                       закончить, скажи "хватит"'

            sessionStorage[user_id]['playing_names'] = True
            sessionStorage[user_id]['last'] = ''
            res['response']['buttons'] = [{'title': 'Хватит', 'hide': True}]
        else:
            res['response']['text'] = 'Я тебя не поняла, повтори пожалуйста'
        sessionStorage[user_id]['used'] = []
        return

    res['response']['text'] = 'Я тебя не поняла, повтори пожалуйста'


def get_city(req):
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.GEO':
            return entity['value'].get('city', None)


def get_greeting():
    greetings = ["Доброе утро", "Добрый день", "Добрый вечер", "Здравствуйте"]
    hour = (datetime.datetime.now().hour + 3) % 24
    i = 3
    if 0 <= hour < 4:
        i = 3
    elif 4 <= hour < 12:
        i = 0
    elif 12 <= hour < 17:
        i = 1
    elif 17 <= hour < 24:
        i = 2

    return greetings[i]


def get_first_name(req):
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.FIO':
            return entity['value'].get('first_name', None)


if __name__ == '__main__':
    app.run()
