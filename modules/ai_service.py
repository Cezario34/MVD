import os
import logging
import requests
from openai import OpenAI
from environs import Env
from typing import Optional

class AIService:

    def __init__(self,
                 api_key: str,
                 model: str = "gpt-4.1-mini"):
        self.api_key=api_key
        self.model=model

        self.http_proxy = 'http://FgtSa8:YupXza@168.80.202.107:8000'
        self.https_proxy= 'http://FgtSa8:YupXza@168.80.202.107:8000'
        self.logger = logging.getLogger(__name__)

    def _apply_proxy_env(self):
        if self.http_proxy:
            os.environ['HTTP_PROXY']  = self.http_proxy
        if self.https_proxy:
            os.environ['HTTPS_PROXY'] = self.https_proxy

    def _clear_proxy_env(self):
        for key in ('HTTP_PROXY', 'HTTPS_PROXY'):
            os.environ.pop(key, None)

    def analyze(self, promt: str) -> str | None:

        os.environ['HTTP_PROXY'] = 'http://FgtSa8:YupXza@168.80.202.107:8000'
        os.environ['HTTPS_PROXY'] = 'http://FgtSa8:YupXza@168.80.202.107:8000'
        models = ["gpt-4.1-mini", "gpt-4.1"]
        try:
            client = OpenAI(api_key=self.api_key)
            for model in models:
                try:
                    response = client.chat.completions.create(
                        model    = model,
                        messages = [{"role":"user","content":promt}],         # передаём ключ здесь
                    )
                    return response.choices[0].message.content
                except Exception as e:
                    self.logger.warning("Ошибка на модели %s: %s", model, e)
                    # попробуем следующую модель
            return None
        finally:
            os.environ.pop('HTTP_PROXY', None)
            os.environ.pop('HTTPS_PROXY', None)

    def select_mvd(
            self,
            options: list[str],
            reg_address: str,
            find: str,
            prompt: Optional[str] = None
        ) -> Optional[str]:
        
        if prompt == None:
            exclude = ("ГУ", "Главное управление")
            filtered = [o for o in options if not any(x in o for x in exclude)]

            prompt = f"""К какому мвд относится {reg_address}?  На сайте мвд ближайшее {find}, а надо выбрать из списка {filtered}. ОТВЕТ ТОЛЬКО МВД ИЗ СПИСКА, ТАК КАК БУДЕТ ДАЛЕЕ ВЫБИРАТЬСЯ ОНО НИКАКИХ КОММЕНТАРИЕВ БОЛЕЕЕ. 
                            Ответ возвращай в виде текста, только 1 вариант. Если не видишь совпадений - 
                            Возвращай слово НЕТ. Особенно это касается городских МВД. 
                            Обязательно проверяй наличие района в городе. Если такого района в городе нет, выбирай городское МВД. Например. если город Ярославль, а район Ростовский, ты не выбираешь МВД Города Ростова, а выбираешь МВД города ЯРОСЛАВЛЬ!
                            Сначала смотри, есть ли совпадение по району у адреса и районного мвд из списка, города тоже должны совпадать.
                            Если нет то смотри выбирай городское. Если город Москва или Санкт-Петербург, особенно важно сопоставить ближайшее мвд и из списка  
                            Если нет совпадение по району и ближайшего МВД. Выбирай городское МВД. Если абсолютно никаких совпадений не найдено верни - НЕТ"""
        answer = self.analyze(prompt)
        return answer.strip() if answer else None


    def answer(self, prompt: str) -> str | None:
        return self.analyze(prompt)