import logging
import time
import sys
import requests


from datetime import date
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
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
from captcha import solve_captcha
from tempfile import NamedTemporaryFile
from loans_cheker import find_files_by_keywords, move_folder, get_loan_id, get_Locality,cleanup_temp_uploads
from urllib.parse import urljoin
from mail_pars import get_code
from config_data import person
from selenium.webdriver.common.keys import Keys
from find_regions import get_code_region, bd
from selenium.common.exceptions import WebDriverException, TimeoutException, InvalidArgumentException, StaleElementReferenceException, ElementClickInterceptedException
from text_appel import get_text
from Find_nearst_MVD import get_mvd
from AI_match import answer_ai
from add_commentory import add_link
import create_folder
from urllib.parse import quote_plus
import undetected_chromedriver as uc

today = date.today()
#ПС
# root_folder = fr"\\Pczaitenov\159\Ежедневная подача\Галимзянова\{current_date} ПС"
root_folder = fr"\\Pczaitenov\159\Ежедневная подача\Галимзянова\17.06.2025 пс"


#ДК
# root_folder = r"\\Pczaitenov\159\ДК. Ежедневная подача\Мезитова\03.06.2025 ДК"
current_date = today.strftime("%d.%m.%Y")
dst_root = fr"\\Pczaitenov\159\Ежедневная подача\Галимзянова\Выполненные\{current_date}\ПС"
unfulfilled_root = fr"\\Pczaitenov\159\Ежедневная подача\Галимзянова\Невыполненные"

keywords = [".docx", ".xlsx", ".pdf", ".docx.doc"]

phone_number = 89600476437

#ПС
static_file_1 = r"\\Pczaitenov\159\Ежедневная подача\Галимзянова\Агентский договор Триумвират - ЭквИта-Капитал.pdf"
static_file_2 = r"\\Pczaitenov\159\Ежедневная подача\Галимзянова\ДОВЕРЕННОСТЬ НА СОТРУДНИКА ГАЛИМЗЯНОВА.pdf"
static_file_3 = r"\\Pczaitenov\159\Ежедневная подача\Галимзянова\Доверенность от Триумвират на Эквиту.pdf"


#ДК
# static_file_1 = r"\\Pczaitenov\159\ДК. Ежедневная подача\Мезитова\ДК Агентский договор Ден. Крепость - Эквита (1) (1).pdf"
# static_file_2 = r"\\Pczaitenov\159\ДК. Ежедневная подача\Мезитова\ДК Доверенность от Денежная крепость на Эквиту.pdf"
# static_file_3 = r"\\Pczaitenov\159\ДК. Ежедневная подача\Мезитова\ДК Мезитова довер.pdf"


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


def screenshot_and_solve(driver, element, filename='captcha.png'):
    element.screenshot(filename)
    print(f"Скриншот капчи сохранён: {filename} \n Происходит обход капчи, просто ожидай дальнейших инструкций")
    return solve_captcha(filename)


def looking_and_solve_capthca():
    captcha_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".captcha-img")))
    captcha_text = screenshot_and_solve(driver, captcha_element)
    if len(captcha_text)<5:
        captcha_text = screenshot_and_solve(driver, captcha_element)
    print("Решение капчи:", captcha_text)

    # # Решение Каптчи
    captcha_input = driver.find_element(By.NAME, "captcha")
    captcha_input.clear()
    captcha_input.send_keys(captcha_text)

def check_info(driver):
    logger.info('Кликаю по заявлению от гражданина')
    checkbox_label2 = WebDriverWait(driver, 100).until(
    EC.element_to_be_clickable((By.CLASS_NAME, "checkbox"))
    ).click()
    button =  WebDriverWait(driver, 60).until(
    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Подать обращение от гражданина')]"))).click()
    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "modal-content")))
    btn_gos_uslugi = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//a[.//img[@alt='Войти через Госуслуги']]"))
    ).click()


def repeat_captcha_block(driver, max_attempts=2):
    """
    Пробует решить капчу, если не получилось — ищет ошибку, запускает автосолвер и кликает снова.
    После max_attempts просит вручную.
    """
    for i in range(max_attempts+1):

        driver.find_element(By.CLASS_NAME, "u-form__sbt").click()

        try:
            # Ждём кнопку подтверждения (если она появилась — успех)
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "confirm_but"))
            )
            print("[SUCCESS] Капча успешно решена, продолжаем.")
            return True
        except TimeoutException:
            # Кнопки нет — ищем ошибку по капче
            try:
                error_block = WebDriverWait(driver, 2).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "b-error_list-item"))
                )
                print("[ERROR] Капча неверна, запускаем повторный обход.")
                try:
                    looking_and_solve_capthca()
                except Exception as e:
                    logger.error('Сервис не отвечает.')
                    logger.info('Сервис обхода капчи не отвечает.')
                    break
                # После автосолва цикл продолжится, будет новая попытка
            except TimeoutException:
                print("[ERROR] Ошибка по капче не обнаружена, возможно другая проблема.")
                break  # Можно выйти или обработать иначе

    input("Проверь ввод капчи, заполни ее в ручную, нажми кнопку ПОДТВЕРДИТЬ и затем вернись в это окно,  Нажав Enter для продолжения...")
    WebDriverWait(driver, 120).until(
        EC.element_to_be_clickable((By.ID, "confirm_but"))
    )
    print("[SUCCESS] Капча введена вручную, продолжаем.")
    return True


try:
    
    options = uc.ChromeOptions()    
    options.add_argument("--window-size=1200,900")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    driver = uc.Chrome(service=ChromiumService(ChromeDriverManager().install()),options=options)
    driver.set_window_size(700, 900)
    driver.execute_script("document.body.style.zoom='80%'")
    wait = WebDriverWait(driver, 15)
    logger.info('Запускаем браузер')
    counter = 0
    while True:
        start = time.time()
        try:
            #Получение номера договора из папки + данные по клиенту
            try:
                loan_id = get_loan_id(root_folder)
                found, folder_path  = find_files_by_keywords(root_folder, keywords)
                logger.info(f'Обрабатываю договор {loan_id}')
            except Exception as e:
                logger.critical(f'Папка не найдена, проверь путь! {e}')
                raise FileNotFoundError
                break

            try:
                fio, birthday, region_id, reg_address = get_code_region(bd['ps'], loan_id)
                logger.info('Вытягиваю данные из бд')
                logger.info(f'Данные по клиенту {fio}, {reg_address}')
            except Exception as e:
                logger.critical(f'Подключение к бд не выполненоо, данные не получены {e}')
                raise ConnectionError
                break
            if any(x is None for x in [fio, birthday, region_id, reg_address]):
                move_folder(folder_path, dst_root)
                logger.error(f'Клиент {loan_id} не проходит по меткам или ОД')
                input('Проверь метки по клиенту и подтверди интером')
                continue
            #Ищем ближайшее мвд
            try:
                template_mvd = get_mvd(reg_address)
                logger.info(f'Ищу ближайшее мвд - {template_mvd}')
            except Exception as e:
                logger.error(f'Ближайшее мвд не найдено! Введи его самостоятельно! и нажми Enter в этом окне!')
                input()



            url = f"https://{region_id}.xn--b1aew.xn--p1ai/request_main"


            try:
                logger.info(f'Пытаюсь подключится к странице {url}')
                driver.get(url)
                html = driver.page_source.lower()
                if "/503.jpg" in driver.page_source:                    
                    logger.warning(f"Страница {url} вернула 503 — пропускаем.")
                    move_folder(folder_path, unfulfilled_root)
                    time.sleep(5)
                    continue
            except (WebDriverException, TimeoutException, InvalidArgumentException) as e:
                if "503" in str(e):
                    logger.error(f"Ошибка 503 при загрузке {url}: {e}")
                    continue
                logger.critical("Ошибка при загрузке страницы:", e)
                raise TimeoutException

            # Обработка базовой страницы, возможно не актуально
            try:
                time.sleep(3)
                checkbox_label = driver.find_element(By.XPATH, "//label[contains(., 'Министерство внутренних дел Российской Федерации')]").click()

                wait = WebDriverWait(driver, 5)
                wait.until(
                    EC.element_to_be_clickable((By.ID, "f"))
                )

                button = driver.find_element(By.ID, "f").click()


            except Exception as e:
                logging.info('Блока выбора обращений нет, идем дальше.')


            #Базовый блок выбора с гос услугами, повторяется.
            try:
                check_info(driver)
            except Exception as e:
                logger.info(f'Блока нет идем дальше {e}')

            if counter == 0:
                try:
                    check_info(driver)

                except Exception as e:
                    logging.info('повторное обращение не требуется')

            #Выбор ближайшего мвд
            try:
                select_elem = driver.find_element(By.CSS_SELECTOR, ".select2-selection")
                select_elem.click()

                
                options = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ul.select2-results__options li"))
                )

                texts = [o.text for o in options]
                ai = answer_ai(texts, template_mvd, reg_address)

                print(f"AI suggests: {ai}")
                if ai == 'НЕТ':
                    #Блок обработки ошибок аи если не найдено ближайшее мвд 
                    logger.error(f'Выбор мвд не удался, не получается найти ближайшее мвд, адрес клиента {reg_address}')
                    query = f'{reg_address} к какому району относится'
                    encoded_query = quote_plus(query)
                    driver.execute_script(f"window.open('https://www.google.com/search?q={encoded_query}');")
                    driver.switch_to.window(driver.window_handles[-1])
                    hand_mvd = input('Выбери мвд руками в браузере и нажми Enter тут')
                    driver.switch_to.window(driver.window_handles[0])
                found = False
                # Теперь ищем элемент с нужным текстом и кликаем
                for _ in range(3):  # Несколько попыток на случай проблем
                    try:
                        # Получаем свежий список элементов каждый раз, если что-то пошло не так
                        options = driver.find_elements(By.CSS_SELECTOR, "ul.select2-results__options li")

                        for opt in options:
                            # Сравнение in с ррезультатом аи (регистронезависимо)
                            if ai.lower() in opt.text.lower():
                                try:
                                    opt.click()
                                    found = True
                                    print(f"Selected: {opt.text}")
                                    break
                                except Exception as e:
                                    print("Клик не удался (перекрыт), скроллим к элементу и пробуем снова...")
                                    logger.info(f'Ошибка {e}')
                                    driver.execute_script("arguments[0].scrollIntoView();", opt)
                                    time.sleep(0.3)
                                    opt.click()
                                    found = True
                                    print(f"Selected after scroll: {opt.text}")
                                    break

                        if found:
                            break  # Выбрали — выходим из внешнего цикла

                    except StaleElementReferenceException:
                        print("Элемент устарел, повторяем поиск...")
                        time.sleep(0.5)
                        continue
            except Exception as e:
                logger.error(f'Выбор мвд не удался, проблема {e}')
                hand_mvd = input('Выбери мвд руками в браузере и нажми интер тут')
            logger.info(f'Адрес регистрации клиента - {reg_address}')
            
            phone_input = driver.find_element(By.ID, "phone_check")
            phone_input.clear()  # если нужно очистить перед вводом
            phone_input.send_keys(phone_number)


            #Ввод емайла
            try:
                wait = WebDriverWait(driver, 60)
                EMAIL_INPUT = wait.until(EC.visibility_of_element_located((By.ID, "email_check")))

                actions = ActionChains(driver)
                actions.move_to_element(EMAIL_INPUT).click().perform()
                driver.execute_script('arguments[0].value = ""', EMAIL_INPUT)
                EMAIL_INPUT.send_keys(person.email)
                logger.info('Вводим майл')
            except Exception as e:
                logger.error(f'Майл не введен, ошибка {e}')

            
            #Должность
            try:
                logger.info('Ввожу название папки и должность.')
                post_input = driver.find_element(By.NAME, "post")
                post_input.send_keys("ООО ПКО ЭКВИТА КАПИТАЛ")
                locality=get_Locality(root_folder)
                # Для ФИО (fio)
                fio_input = driver.find_element(By.NAME, "fio")
                fio_input.send_keys(locality)
            except Exception as e:
                logger.error(f'Должность и фио не выбраны, записываю ошибку в лог {e}')
                input(f'Введи в ручную и нажми Enter')

            #Обращение    
            try:
                TEXT = get_text(locality=locality,fio=fio,birthday=birthday)
                logger.info('Формирую текст обращения')
            except:
                logger.error('Текст обращения не сформирован! Введи в ручную и нажми Enter')
                input()
            TEXT_INPUT = wait.until(
                EC.visibility_of_element_located((By.CLASS_NAME, "textarea"))
            )
            TEXT_INPUT.send_keys(TEXT)

            #Поиск капчи
            try:
                looking_and_solve_capthca() 
            except Exception as e:
                logger.error(f'Проблема с капчей.{e}')

            try:
            # Ищем где загружать файл.
                file_input = driver.find_element(By.ID, "fileupload-input")
                found, folder_path  = find_files_by_keywords(root_folder, keywords)
                found.extend([static_file_1,static_file_2,static_file_3])
            except Exception as e:
                logger.error('Пути не найдены, загрузи файлы самостоятельно')
                input('Загружены?')
                
            for i in found:
            # Отправляем путь к файлу
                file_input.send_keys(i)
                WebDriverWait(driver, 30).until(
                    lambda d: d.find_element(By.ID, "fileupload-list").value_of_css_property("opacity") == '1'
                )
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "half_link"))
                )
            try:
                WebDriverWait(driver, 10).until(
                    lambda d: len(d.find_elements(By.CLASS_NAME, "half_link")) == 7
                )
            except:
                finish_upload = input('Подтверди что все 7 файлов загружены и нажми Enter..')

            cleanup_temp_uploads()

            #Проверка всего блока перед отправкой документов + перепрохождение капчи
            input("Проверь корретность данных. Нажми Enter для продолжения...")
            repeat_captcha_block(driver)
            driver.find_element(By.CLASS_NAME, "u-form__sbt").click()

            #Отправить код на почту
            sending_letter = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "confirm_but"))
            ).click()


            #Получение кода из письма + подтверждение
            time.sleep(3)
            logger.info('Отправлено письмо на почту, вытягиваю код. Просто жди.')
            code = get_code()
            email_code_input = wait.until(
                EC.visibility_of_element_located((By.CLASS_NAME, "confirm-mail"))
            )
            email_code_input.send_keys(code)
            logger.info('код введен')

            #Подтверждение кода
            button_confirm_email = driver.find_element(By.ID, "confirm_mail").click()

            #Финальная отправка
            checkbox = driver.find_element(By.ID, 'correct')
            driver.execute_script("arguments[0].click();", checkbox)
            try:
                button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "form-submit"))
                )
                driver.execute_script("arguments[0].click();", button)
            except Exception as e:
                logger.error(f"Не удалось кликнуть по кнопке 'Отправить': {e}")

            #Финальный блок с отправкой заявления
            input('Нажми кнопку ОТПРАВИТЬ, а затем нажми Enter')

            #Получение кода, перемещение папок, запись ссылки в эксель файл.
            counter += 1
            try:
                logger.info(f'Номер договора {loan_id}')
                logger.info('Пробую получить и записать ссылку')
                p_code = driver.find_element(By.XPATH, "//p[contains(text(), 'Код проверки статуса обращения')]")
                status_code = p_code.find_element(By.TAG_NAME, "b").text.strip()
                logger.info(f'{status_code} код проверки')
                link = f'https://{region_id}.xn--b1aew.xn--p1ai/request_main/check/?status={status_code}'
                logger.info(f'link {link}')
                logger.info('Пробую записать в файл')
                add_link(loan_id, link)
                logger.info('Записал в файл. Перемещаю папки')
                move_folder(folder_path, dst_root)
                check_final = input('Зарегистрируй комментарий и после нажми интер чтобы цикл пошел заново')
            except Exception as e:
                logger.error(f'Ошибка! Не получилось подтвердить и записать! {e}')
                logger.info(f'Номер договора {loan_id}')
                input('Зарегистрируй комментарий и после нажми Enter чтобы цикл пошел заново')
                move_folder(folder_path, dst_root)
            end = time.time()
            print(f"Время выполнения блока: {end - start:.2f} секунд")


        except Exception as e:
            logger.exception(f"Ошибка в процессе: {e}")
            with open("error.log", "a", encoding="utf-8") as f:
                        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] СКРИПТ УПАЛ! . Ошибка: {e}\n")
            driver.quit()
            logger.info("Браузер закрыт.")

except Exception as e:
    logger.critical(f'Браузер не запущен! {e}')
    raise BaseException

finally:
    driver.quit()
    logger.info("Браузер закрыт.")