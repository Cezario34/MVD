from twocaptcha import TwoCaptcha
from environs import Env

env_path=r"\\Pczaitenov\159\Служебная папка\.env"
env = Env()
env.read_env(env_path)
API = env('API_KEY')


def solve_captcha(path):
    solver = TwoCaptcha(API)
    result = solver.normal(path)
    return result['code']