from twocaptcha import TwoCaptcha
from environs import Env

env_path=r"\\Pczaitenov\159\Служебная папка\.env"
env = Env()
env.read_env(env_path)
API = env('API_KEY')


def solve_captcha(path, max_attempts=5):
    solver = TwoCaptcha(API)
    for attempt in range(max_attempts):
        result = solver.normal(path)
        code = result.get('code', '')
        if len(code) > 0 and code != 'white':
            return code
        else:
            # Сообщаем сервису, что капча не решена
            solver.report(result.get('captchaId', ''), False)
            print(f'Капча не решена, попытка {attempt + 1} из {max_attempts}')
    # Если все попытки неудачны — бросаем ошибку или возвращаем None
    return None

        