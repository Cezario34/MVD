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