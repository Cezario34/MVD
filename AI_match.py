
import datetime
import sys
import os
sys.path.append(r'C:\Users\gluhovva\MyConfig')
sys.path.append(r'C:\Users\gluhovva\MyConfig\query')

from google import genai

import os
import requests
from google.genai import types
from environs import Env


env = Env()
env.read_env(override=True)
api_key=env('API_KEY_GOOGLE')

def image_analityc(text):
    try:
        os.environ['HTTP_PROXY'] = 'http://FgtSa8:YupXza@168.80.202.107:8000'
        os.environ['HTTPS_PROXY'] = 'http://FgtSa8:YupXza@168.80.202.107:8000'

        proxies = {
        "http": "http://FgtSa8:YupXza@168.80.202.107:8000",
        "https": "http://FgtSa8:YupXza@168.80.202.107:8000"
        }

        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
        model="gemini-2.5-flash-preview-04-17",
        contents=[text])
        os.environ.pop('HTTP_PROXY', None)
        os.environ.pop('HTTPS_PROXY', None)

    except Exception as e:
        channel_id = 'ahem6wmypjd4iet7msgxew34br'
        print(f'Ошибка! {e}')
        
    return response.text

def answer_ai(lists: list, find: str) -> str: 
    filtered = [item for item in lists if "ГУ" not in item and "Главное управление" not in item]
    answer = image_analityc(f'К какому мвд относится {find} из списка {filtered} Ответ только название РАЙОННОГО МВД, никаких комментариев более. Главное управление, ГУ, выбирать запрещено. Если видишь совпадение по районам - выбирай районное мвд')
    return answer
