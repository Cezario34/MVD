import os
import logging
from openai import OpenAI
from environs import Env


class AIService:

    def __init__(self,
                 api_key: str,
                 model: str = "gpt-4.1-mini"):
        self.api_key=api_key
        self.model=model
        self.logger = logging.getLogger(__name__)
        self.client = OpenAI(api_key=self.api_key)

    def _apply_proxy_env(self):
        if self.http_proxy:
            os.environ['HTTP_PROXY']  = 'http://FgtSa8:YupXza@168.80.202.107:8000'
        if self.https_proxy:
            os.environ['HTTPS_PROXY'] = 'http://FgtSa8:YupXza@168.80.202.107:8000'

    def _clear_proxy_env(self):
        for key in ('HTTP_PROXY', 'HTTPS_PROXY'):
            os.environ.pop(key, None)

    def analyze(self, promt: str) -> str | None:

        self._apply_proxy_env()
        models = ["gpt-4.1-mini", "gpt-4.1"]
        try:
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
        except Exception as e:
            self.logger.error(f"Ошибка при обращении к OpenAI: {e}")
            return None
        finally:
            self._clear_proxy_env()

    def select_mvd(
            self,
            options: list[str],
            template: str,
            reg_address: str,
            find: str
    ) -> str:
        
        exclude = ("ГУ", "Главное управление")
        filtered = [o for o in options if not any(x in o for x in exclude)]

        prompt = f"""К какому мвд относится {reg_addres}?  На сайте мвд ближайшее {find}, а надо выбрать из списка {filtered}. ОТВЕТ ТОЛЬКО МВД ИЗ СПИСКА, ТАК КАК БУДЕТ ДАЛЕЕ ВЫБИРАТЬСЯ ОНО НИКАКИХ КОММЕНТАРИЕВ БОЛЕЕЕ. 
                         Ответ возвращай в виде текста, только 1 вариант. Если не видишь совпадений - 
                         Возвращай слово НЕТ. Особенно это касается городских МВД. 
                        Обязательно проверяй наличие района в городе. Если такого района в городе нет, выбирай городское МВД.
                         Сначала смотри, есть ли совпадение по району у адреса и районного мвд из списка, города тоже должны совпадать. Т.е если город Ярославль, а район Ростовский, ты не выбираешь МВД Города Ростова, а выбираешь ЯРОСЛАВЛЬ! Точность города ВАЖНА!
                         Если нет то смотри выбирай городское. Если город Москва или Санкт-Петербург, особенно важно сопоставить ближайшее мвд и из списка  
                        Если нет совпадение по району и ближайшего МВД. Выбирай городское МВД. Если абсолютно никаких совпадений не найдено верни - НЕТ"""
        answer = self.analyze(promt)
        return answer.strip() if answer else None