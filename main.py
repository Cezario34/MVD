import logging
import time
import sys
import requests


from environs import Env
from log_filters import ErrorLogFilter, CriticalLogFilter, DebugWarningLogFilter
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromiumService
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from regions import regions_reversed
from captcha import solve_captcha
from tempfile import NamedTemporaryFile

from urllib.parse import urljoin

file_path1=r"C:\Users\gluhovva\Downloads\credit-detail_5b41907b-30bc-4ca1-9d76-db76b8a0d393.xlsx"
file_path2=r"C:\Users\gluhovva\Downloads\5b41907b-30bc-4ca1-9d76-db76b8a0d393_6-295ГЭС ПС_Объяснение_Сальникова Чулпан Фаргатовна_Галимзянова_.docx"
file_path3=r"C:\Users\gluhovva\Downloads\5b41907b-30bc-4ca1-9d76-db76b8a0d393_b2p_payment.pdf"




def screenshot_and_solve(driver, element, filename='captcha.png'):
    element.screenshot(filename)
    print(f"Скриншот капчи сохранён: {filename}")
    return solve_captcha(filename)



env = Env()
env.read_env()


TEXT = 'Абракадабра'

LOGIN = env('LOGIN')
PASSWORD = env('PASSWORD')
EMAIL = env('EMAIL')

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


formatter_1 = logging.Formatter(
    fmt='[%(asctime)s] #%(levelname)-8s %(filename)s:'
        '%(lineno)d - %(name)s:%(funcName)s - %(message)s'
)

formatter_2 = logging.Formatter(
    fmt='[%(asctime)s] #%(levelname)-8s - %(message)s'
)

error_file = logging.FileHandler('error.log', 'w', encoding='utf-8')
error_file.setLevel(logging.DEBUG)
error_file.addFilter(ErrorLogFilter())
error_file.setFormatter(formatter_1)

stdout = logging.StreamHandler(sys.stdout)
stdout.addFilter(DebugWarningLogFilter())
stdout.setFormatter(formatter_2)

stderr = logging.StreamHandler()
critical_file = logging.FileHandler('critical.log', mode='w', encoding='utf-8')
critical_file.setFormatter(fmt=formatter_1)
critical_file.addFilter(CriticalLogFilter())

logger.addHandler(stderr)
logger.addHandler(critical_file)
logger.addHandler(stdout)
logger.addHandler(error_file)







with webdriver.Chrome(service=ChromiumService(ChromeDriverManager().install())) as driver:
    logger.debug('Запускаем браузер')
    driver.get("https://xn--b1aew.xn--p1ai/request_main")
    time.sleep(3)
    checkbox_label = driver.find_element(By.XPATH, "//label[contains(., 'Министерство внутренних дел Российской Федерации')]").click()

    wait = WebDriverWait(driver, 10)
    wait.until(
        EC.element_to_be_clickable((By.ID, "f"))
    )
    # 3. Теперь кликаем по кнопке
    button = driver.find_element(By.ID, "f").click()

    checkbox_label2 = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "checkbox"))
    ).click()

    button = driver.find_element(By.XPATH, "//button[contains(text(), 'Подать обращение от гражданина')]").click()

    try:
        wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "modal-content")))
        btn_gos_uslugi = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[.//img[@alt='Войти через Госуслуги']]"))
        ).click()
    except TimeoutException:
        with open("debug.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
    time.sleep(5)
    inputs = driver.find_elements(By.TAG_NAME, "input")
    for inp in inputs:
        print(inp.get_attribute("outerHTML"))

    login_input = wait.until(
        EC.visibility_of_element_located((By.ID, "login"))
    )
    login_input.send_keys(LOGIN)
    password_input = wait.until(
        EC.visibility_of_element_located((By.ID, "password"))
    )
    password_input.send_keys(PASSWORD)
    login_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Войти')]"))
    )
    login_button.click()
    time.sleep(3)
    short_code=input('Вставьте 6 код/n')
    code_input = wait.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "esia-code-input input"))
    )
    code_input.send_keys(short_code)

    EMAIL_INPUT = wait.until(
        EC.visibility_of_element_located((By.ID, "email_check"))
    )
    EMAIL_INPUT.clear()
    EMAIL_INPUT.send_keys(EMAIL)

    TEXT_INPUT = wait.until(
        EC.visibility_of_element_located((By.CLASS_NAME, "textarea"))
    )
    TEXT_INPUT.send_keys(TEXT)

    captcha_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".captcha-img")))
    captcha_text = screenshot_and_solve(driver, captcha_element)
    print("Решение капчи:", captcha_text)

    # Введи капчу
    captcha_input = driver.find_element(By.NAME, "captcha")
    captcha_input.clear()
    captcha_input.send_keys(captcha_text)
    file_input = driver.find_element(By.ID, "fileupload-input")
# 3. Отправляем путь к файлу
    file_input.send_keys(file_path1)
    file_input.send_keys(file_path2)
    file_input.send_keys(file_path3)
    # # 4. Вставляем капчу
    # input_field = driver.find_element(By.NAME, "captcha")
    # input_field.clear()
    # input_field.send_keys(captcha_text)
    time.sleep(150)