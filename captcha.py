from twocaptcha import TwoCaptcha
from environs import Env
import os
import time


env_path=r"\\Pczaitenov\159\Служебная папка\.env"
env = Env()
env.read_env(env_path,override=True)
API = env('API_CAPTCHA')



def solve_captcha(path, max_attempts=5):
    os.environ['HTTP_PROXY'] = 'http://FgtSa8:YupXza@168.80.202.107:8000'
    os.environ['HTTPS_PROXY'] = 'http://FgtSa8:YupXza@168.80.202.107:8000'
    solver = TwoCaptcha(API)
    try:
        for attempt in range(1, max_attempts + 1):
            try:
                result = solver.normal(path)
                code = result.get('code', '')
                if len(code) > 0 and code != 'white':
                    print(f'[OK] Капча решена на попытке {attempt}')
                    return code
                else:
                    solver.report(result.get('captchaId', ''), False)
                    print(f'Капча не решена, попытка {attempt} из {max_attempts}')
            except Exception as e:
                print(f"[ERROR] Ошибка соединения с сервисом (попытка {attempt}): {e}")
                time.sleep(2)
                continue
        print('Все попытки решения капчи исчерпаны')
        return None
    finally:
        os.environ.pop('HTTP_PROXY', None)
        os.environ.pop('HTTPS_PROXY', None)
