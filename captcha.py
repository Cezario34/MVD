from twocaptcha import TwoCaptcha
from environs import Env

env = Env()
env.read_env()
API = env('API_KEY')


def solve_captcha(path):
    solver = TwoCaptcha(API)
    result = solver.normal(path)
    return result['code']