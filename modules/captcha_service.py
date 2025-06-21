import os
import time
import logging

from twocaptcha import TwoCaptcha


class CaptchaService:
    def __init__(self, api_key: str, max_attempts: int = 5):
        self.api_key = api_key
        self.max_attempts = max_attempts
        self.logger = logging.getLogger(__name__)

    def solve(self, image_path: str) -> str | None: 

        os.environ['HTTP_PROXY'] = 'http://FgtSa8:YupXza@168.80.202.107:8000'
        os.environ['HTTPS_PROXY'] = 'http://FgtSa8:YupXza@168.80.202.107:8000'

        solver = TwoCaptcha(self.api_key)

        try:
            for attempt in range(1, self.max_attempts +1):
                try:
                    result = solver.normal(image_path)
                    code = result.get('code', '')
                    if len(code) > 0 and code != 'white':
                        print(f'[OK] Капча решена на попытке {attempt}')
                        return code
                    else:
                        solver.report(result.get('captchaId', ''), False)
                        print(f'Капча не решена, попытка {attempt} из {max_attempts}')
                except Exception as e:
                    self.logger.error(f"Ошибка в запросе к 2Captcha (попытка {attempt}): {e}")
                    time.sleep(2)
                    continue
            self.logger.error("Все попытки решения капчи исчерпаны")
            return None
        finally:
            for k in ("HTTP_PROXY", "HTTPS_PROXY"):
                os.environ.pop(k, None)

