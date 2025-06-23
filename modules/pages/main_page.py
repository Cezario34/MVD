from selenium.common.exceptions import WebDriverException,StaleElementReferenceException,  TimeoutException,ElementNotVisibleException, InvalidArgumentException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time

class MainPage():


    def __init__(
        self,
        driver,
        wait,
        logger
    ):

        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        self.logger = logger
        self._list_locator = (By.CSS_SELECTOR, "ul.select2-results__options li")
        self.cnt_file = 7

    def click_list_mvd(self):
        try:
            select_elem = self.driver.find_element(By.CSS_SELECTOR, ".select2-selection")
            select_elem.click()
        except:
            raise ElementNotVisibleException


    def get_list_mvd(self):

        options = self.wait.until(
            EC.presence_of_all_elements_located(self._list_locator)
        )
        texts = [o.text for o in options]
        return texts

    def select_mvd(self, answer_ai):
        options = self.wait.until(
            EC.presence_of_all_elements_located(self._list_locator)
        )
        found = False
        # Теперь ищем элемент с нужным текстом и кликаем
        for _ in range(3):  # Несколько попыток на случай проблем
            try:
                # Получаем свежий список элементов каждый раз, если что-то пошло не так
                options = self.wait.until(
                    EC.presence_of_all_elements_located(self._list_locator))

                for opt in options:
                    # Сравнение in с ррезультатом аи (регистронезависимо)
                    if answer_ai.lower() in opt.text.lower():
                        try:
                            opt.click()
                            found = True
                            print(f"Selected: {opt.text}")
                            break
                        except Exception as e:
                            print("Клик не удался (перекрыт), скроллим к элементу и пробуем снова...")
                            self.logger.info(f'Ошибка {e}')
                            self.driver.execute_script("arguments[0].scrollIntoView();", opt)
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
    
    def phone_input(self,phone_number):
        phone_input = self.driver.find_element(By.ID, "phone_check")
        phone_input.clear()  # если нужно очистить перед вводом
        phone_input.send_keys(phone_number)
        self.logger.info('Вводим телефон')
    
    def input_email(self, email):
        email_input = self.wait.until(EC.visibility_of_element_located((By.ID, "email_check")))
        actions = ActionChains(self.driver)
        actions.move_to_element(email_input).click().perform()
        self.driver.execute_script('arguments[0].value = ""', email_input)
        email_input.send_keys(email)
        self.logger.info('Вводим почту')

    def input_post(self):
        self.logger.info('Ввожу название папки и должность.')
        post_input = self.driver.find_element(By.NAME, "post")
        post_input.send_keys("ООО ПКО ЭКВИТА КАПИТАЛ")

    def input_fio(self, locality, bd):
        fio_input = self.driver.find_element(By.NAME, "fio")
        fio_input.send_keys(locality+bd)

    def text_input(self, text):
        text_input = self.wait.until(
            EC.visibility_of_element_located((By.CLASS_NAME, "textarea")))
        text_input.send_keys(text)
    
    def input_files(self, found):
        static_file_1 = r"\\Pczaitenov\159\Ежедневная подача\Галимзянова\Агентский договор Триумвират - ЭквИта-Капитал.pdf"
        static_file_2 = r"\\Pczaitenov\159\Ежедневная подача\Галимзянова\ДОВЕРЕННОСТЬ НА СОТРУДНИКА ГАЛИМЗЯНОВА.pdf"
        static_file_3 = r"\\Pczaitenov\159\Ежедневная подача\Галимзянова\Доверенность от Триумвират на Эквиту.pdf"
        found.extend([static_file_1,static_file_2,static_file_3])
        try:
            file_input = self.driver.find_element(By.ID, "fileupload-input")
            for i in found:
                # Отправляем путь к файлу
                    file_input.send_keys(i)
                    self.wait.until(
                        lambda d: d.find_element(By.ID, "fileupload-list").value_of_css_property("opacity") == '1'
                    )
                    self.wait.until(
                        EC.presence_of_element_located((By.CLASS_NAME, "half_link"))
                    )
        except Exception as e:
            self.logger.error('Ошибка при загрузке файла!')

    def check_len_files(self):
        try:
            self.wait.until(
                lambda d: len(d.find_elements(By.CLASS_NAME, "half_link")) == self.cnt_file)
        except:
            raise FileNotFoundError


    def find_capthca(self):
        try:
            captcha_element = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".captcha-img")))
            return captcha_element
        except:
            raise ElementNotVisibleException

    def screenshot_and_solve(self, element, filename='captcha.png'):
        try:
            self.driver.execute_script("document.body.style.zoom='100%'")
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)

            self.wait.until(
            EC.visibility_of(element))
        except:
            raise ElementNotVisibleException

        element.screenshot(filename)
        self.logger.info(f"Скриншот капчи сохранён: {filename} \n Происходит обход капчи, просто ожидай дальнейших инструкций")
        return filename

    def input_captcha(self, text_captcha):
        captcha_input = self.driver.find_element(By.NAME, "captcha")
        captcha_input.clear()
        captcha_input.send_keys(text_captcha)

    def accept_the_application(self):
        self.driver.find_element(By.CLASS_NAME, "u-form__sbt").click()


    def find_error_capthca(self):
        error_block = WebDriverWait(driver, 3).until(
        EC.presence_of_element_located((By.CLASS_NAME, "b-error_list-item"))
            )

    def captcha_src(self):
        element = self.find_capthca()
        captcha_path = self.screenshot_and_solve(element)
        return captcha_path