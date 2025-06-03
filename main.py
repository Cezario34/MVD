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
from loans_cheker import find_files_by_keywords, move_folder
from urllib.parse import urljoin
from mail_pars import get_code


root_folder = r"C:\Users\gluhovva\Desktop\Folder1"
dst_root = r"C:\Users\gluhovva\Desktop\Folder 2"
keywords = ["Логика", "Слабые", "comeback", "подтверждение", "справка"]  # твои ключевые слова



def screenshot_and_solve(driver, element, filename='captcha.png'):
    element.screenshot(filename)
    print(f"Скриншот капчи сохранён: {filename}")
    return solve_captcha(filename)


def looking_and_solve_capthca():
    captcha_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".captcha-img")))
    captcha_text = screenshot_and_solve(driver, captcha_element)
    print("Решение капчи:", captcha_text)

    # # Решение Каптчи
    captcha_input = driver.find_element(By.NAME, "captcha")
    captcha_input.clear()
    captcha_input.send_keys(captcha_text)



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




driver = webdriver.Chrome(service=ChromiumService(ChromeDriverManager().install()))
wait = WebDriverWait(driver, 15)

try:
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
    #Блок  авторизации гос услуг
    try:
        wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "modal-content")))
        btn_gos_uslugi = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[.//img[@alt='Войти через Госуслуги']]"))
        ).click()
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
        short_code=input('Вставьте 6 код\n')
        code_input = wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "esia-code-input input"))
        )
        code_input.send_keys(short_code)
    except TimeoutException:
        logging.info('Авторизация не требуется')

    #Ввод емайла
    EMAIL_INPUT = wait.until(
        EC.visibility_of_element_located((By.ID, "email_check"))
    )
    EMAIL_INPUT.clear()
    EMAIL_INPUT.send_keys(EMAIL)

    TEXT_INPUT = wait.until(
        EC.visibility_of_element_located((By.CLASS_NAME, "textarea"))
    )
    TEXT_INPUT.send_keys(TEXT)

    # #Поиск капчи
    try:
        looking_and_solve_capthca()
    except:
        logger.info('Проблема с капчей. Введи руками или дождись следующего шага')

    # #Ищем где загружать файл.
    file_input = driver.find_element(By.ID, "fileupload-input")

    found,folder_path  = find_files_by_keywords(root_folder, keywords)
    for i in found:
    # 3. Отправляем путь к файлу
        print(i)
        file_input.send_keys(i)
        time.sleep(5)
    
    complete_button = driver.find_element(By.CLASS_NAME, "u-form__sbt").click()
    
    try:
        WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.CLASS_NAME, "b-error_list-item"))
        )
        print("Ошибка! Капча неверна")
        looking_and_solve_capthca()
        complete_button = driver.find_element(By.CLASS_NAME, "u-form__sbt").click()

    except TimeoutException:
        print("Ошибки нет, идем дальше")
    
    sending_letter = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "confirm_but"))
    ).click()

    time.sleep(10)
    check_up_email = input('Код пришел? \n')
    code = get_code()

    email_code_input = wait.until(
        EC.visibility_of_element_located((By.CLASS_NAME, "confirm-mail"))
    )
    email_code_input.send_keys(code)
    logger.info('код введен')

    button_confirm_email = driver.find_element(By.ID, "confirm_mail").click()
    
    driver.find_element(By.CSS_SELECTOR, "label.n-checkbox").click()

    # button_confirm_loan = driver.find_element(By.ID, "form-submit").click()
    # link = driver.find_element(By.XPATH, "//a[contains(@href, 'request_main/check')]")
    # print(link.get_attribute('href'))    
    
    # move_folder(folder_path, dst_root)

    
   
    time.sleep(150)

except Exception as e:
    logger.exception(f"Ошибка в процессе: {e}")
    with open("error.log", "a", encoding="utf-8") as f:
                f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] СКРИПТ УПАЛ! . Ошибка: {e}\n")

finally:
    driver.quit()
    logger.info("Браузер закрыт.")