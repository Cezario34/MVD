
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
        models = ["gpt-4.1-mini", "gpt-4.1"]
        for model in models:
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": text}]
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"Ошибка на модели {model}: {e}")
                continue  # пробуем следующую модель


        os.environ.pop('HTTP_PROXY', None)
        os.environ.pop('HTTPS_PROXY', None)

    except Exception as e:
        print('Ошибка:', e)
        return None

def answer_ai(lists: list = None, find: str = None, reg_addres: str = None, promt: str = None) -> str: 
    exclude = ("ГУ", "Главное управление")
    if promt is None:
        filtered = [item for item in lists if not any(x in item for x in exclude)]
        promt = f"""К какому мвд относится {reg_addres}?  На сайте мвд ближайшее {find}, а надо выбрать из списка {filtered}. ОТВЕТ ТОЛЬКО МВД ИЗ СПИСКА, ТАК КАК БУДЕТ ДАЛЕЕ ВЫБИРАТЬСЯ ОНО НИКАКИХ КОММЕНТАРИЕВ БОЛЕЕЕ. 
                            Ответ возвращай в виде текста, только 1 вариант. Если не видишь совпадений - 
                            Возвращай слово НЕТ. Особенно это касается городских МВД. 
                            
                            Сначала смотри, есть ли совпадение по району у адреса и районного мвд из списка, Обязательное требование - города тоже должны совпадать. Т.е если город Ярославль, а район Ростовский, ты не выбираешь МВД Города Ростова, а выбираешь МВД г.ЯРОСЛАВЛЬ! Точность города ВАЖНА!
                            Если нет то смотри выбирай городское. Если город Москва или Санкт-Петербург, особенно важно сопоставить ближайшее мвд и из списка  
                            Если нет совпадение по району и ближайшего МВД. Выбирай городское МВД. Если абсолютно никаких совпадений не найдено верни - НЕТ"""

    answer = image_analityc(promt)

    return answer
