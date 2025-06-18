
import datetime
import sys
import os
sys.path.append(r'C:\Users\gluhovva\MyConfig')
sys.path.append(r'C:\Users\gluhovva\MyConfig\query')

from google import genai

import os
import requests
from environs import Env
from openai import OpenAI


env_path=r"\\Pczaitenov\159\Служебная папка\.env"
env = Env()
env.read_env(env_path,override=True)

def image_analityc(text):
    try:
        os.environ['HTTP_PROXY'] = 'http://FgtSa8:YupXza@168.80.202.107:8000'
        os.environ['HTTPS_PROXY'] = 'http://FgtSa8:YupXza@168.80.202.107:8000'

        proxies = {
        "http": "http://FgtSa8:YupXza@168.80.202.107:8000",
        "https": "http://FgtSa8:YupXza@168.80.202.107:8000"
        }
        client = OpenAI(api_key=env('API_KEY'))  

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "user", "content": text}
            ]
        )

        os.environ.pop('HTTP_PROXY', None)
        os.environ.pop('HTTPS_PROXY', None)

        return response.choices[0].message.content
    except Exception as e:
        print('Ошибка:', e)
        return None

def answer_ai(lists: list, find: str, reg_addres: str) -> str: 
    exclude = ("ГУ", "Главное управление")
    filtered = [item for item in lists if not any(x in item for x in exclude)]
    prompt = f"""К какому мвд относится {find} из списка {filtered}. ОТВЕТ ТОЛЬКО МВД ИЗ СПИСКА, ТАК КАК БУДЕТ ДАЛЕЕ ВЫБИРАТЬСЯ ОНО НИКАКИХ КОММЕНТАРИЕВ БОЛЕЕЕ. 
                         Ответ возвращай в виде текста, только 1 вариант. Если не видишь совпадений - 
                         Возвращай слово НЕТ. Особенно это касается городских МВД. 
                         Сначала смотри, есть ли совпадение по районному мвд.
                        Если нет совпадение по району. Выбирай городское МВД."""

    answer = image_analityc(prompt)

    return answer
