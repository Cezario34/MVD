import time
import logging
import threading


from modules.pages import WelcomePage, FinalPage, MainPage
import undetected_chromedriver as uc
from selenium.common.exceptions import (
    WebDriverException, TimeoutException,
    InvalidArgumentException, ElementNotVisibleException,
    NoSuchElementException
)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from modules.text_appel import get_text
from typing import Callable


class LoanProcessor:

    def __init__(self, root_folder: str, dst_root: str,
                unfulfilled_root: str, keywords: list[str],
                driver_kwargs: dict,
                report_excel: "modules.report_service.ReportService",
                captcha_service: "modules.captcha_service.CaptchaService",
                ai_answer: "modules.ai_service.AIService",
                mvd: "modules.mvd_service.MvdService",
                db_service: "modules.db_service.LoanDataService",
                mail: "modules.mail_parser.MailCode",
                file_service: "modules.files_service.FileService",
                bd: str):
        
        self.root_folder = root_folder
        self.unfulfilled_root = unfulfilled_root
        self.dst_root = dst_root
        self.driver_kwargs = driver_kwargs
        self.report_excel = report_excel
        self.captcha_service = captcha_service
        self.ai_answer = ai_answer
        self.mvd = mvd
        self.keywords = keywords
        self.db_service = db_service
        self.file_service = file_service
        self.logger = logging.getLogger(__name__)
        self.counter = 0
        self.phone_number =89600476437
        self.email ='operation3@ekvitakapital.ru'
        self.mail = mail
        self.bd = bd
        self._wait_for_continue = threading.Event()
        self._stop_event = threading.Event()
        self._on_pause: Callable[[str], None] = lambda prompt: None  
        self._skip_event =  threading.Event()

    def init_browser(self):
        self.driver = uc.Chrome(**self.driver_kwargs)
        self.driver.set_window_size(800, 1200)
        self.wait = WebDriverWait(self.driver, 15)

        self.welcome = WelcomePage(self.driver, self.logger)
        self.main    = MainPage   (self.driver, self.wait, self.logger)
        self.final   = FinalPage  (self.driver, self.wait, self.logger)


    def _pause(self, prompt: str) -> None:
        """Останавливает процессор до нажатия «Продолжить» в GUI."""
        if getattr(self, "_stop_event", None) and self._stop_event.is_set():
            raise RuntimeError("Процесс остановлен пользователем")
        self._wait_for_continue.clear()
        self._on_pause(prompt)
        self._wait_for_continue.wait()

    def _handle_skip(self, folder_path):
        """
        Если пользователь нажал «Пропустить» — переместить папку и сбросить флаг.
        Возвращает True, если мы действительно пропустили, тогда в цикле нужно continue.
        """
        if self._skip_event.is_set():
            self.file_service.move_folder(folder_path, self.unfulfilled_root)
            self.logger.warning("Договор пропущен пользователем")
            self._skip_event.clear()
            return True
        return False


    def run(self,
            pause_event: threading.Event,
            stop_event: threading.Event,
            skip_event: threading.Event):
    
        self._wait_for_continue = pause_event
        self._stop_event      = stop_event 
        self._skip_event = skip_event
        self.init_browser()
        while not self._stop_event.is_set():
            start = time.time()

            #Вытягиваем лоан ид из папки + пути к файлам.
            try:
                loan_id = self.file_service.get_loan_id(self.root_folder)
                found, folder_path = self.file_service.find_files_by_keywords(self.root_folder)
                self.logger.warning(f'Обрабатываю договор {loan_id}')
            except Exception as e:
                self.logger.critical(f'Папка не найдена, проверь путь! {e}')
                raise FileNotFoundError

            
            try:
                ps_conn = self.db_service.remote_db_map['ps']
                fio, birthday, region_id, reg_address = \
                    self.db_service.get_code_region("dk", loan_id)
                self.logger.info('Вытягиваю данные из бд')
                self.logger.warning(f'Данные по клиенту {fio}, {reg_address}')
            except Exception as e:
                self.logger.critical(f'Подключение к бд не выполненоо, данные не получены {e}')
                raise ConnectionError

            
            #Замена региона, пропуск пустых данных в бд
            if any (x is None for x in [fio, birthday, reg_address]):
                self.logger.error(f'Клиент {loan_id} не проходит по меткам или ОД')
                self._pause("Проверь метки, ОД и нажмите «Продолжить». Договор будет помещен в невыполненные")
                self.file_service.move_folder(folder_path, self.unfulfilled_root)
                continue
            elif region_id is None:
                region_id = self.ai_answer.answer(promt = f"""Какой регион {reg_address}? Верни только номер региона.Возвращать что либо другое кроме номера запрещено!
                                        Данные пойдут дальше""")

            #Логика приветственной страницы                           
            try:
                self.welcome.open(region_id)
            except TimeoutException:
                self.logger.critical("Ошибка при загрузке страницы")
                self.file_service.move_folder(folder_path, self.unfulfilled_root)
                continue
            except WebDriverException:
                self.logger.error("Ошибка при загрузке страницы 503 ошибка")
                self.file_service.move_folder(folder_path, self.unfulfilled_root)
                continue
            time.sleep(10)
            if self._handle_skip(folder_path):
                continue
            
            try:
                if self.counter == 0:
                    self.welcome.gos_auth_page()
                    self.welcome.click_gos_service()
                    self.welcome.gos_auth_page()
                else:
                    self.welcome.gos_auth_page()
            except Exception as e:
                self.logger.error("Авторизация на госуслугах не удалась", exc_info=True)
                    

            self.logger.warning('Обрабатываю информацию ближайшего мвд, ожидай.')

            try:
                self.main.click_list_mvd()
            except ElementNotVisibleException:
                self.logger.error('Список мвд не найден')

            try:
                list_mvd = self.main.get_list_mvd()
            except TimeoutException:
                # self.logger.warning("Список МВД не загрузился за отведённое время, перейдите к ручному выбору")
                list_mvd = [] 

            try:
                find  = self.mvd.select_mvd(reg_address)
            except Exception as exp:
                self.logger.error(f'Ошибка при получении ближайшего МВД! {exp}')
                find = ""
            try:
                answer = self.ai_answer.select_mvd(
                    options=list_mvd,
                    reg_address=reg_address,
                    find=find
                )
            except Exception as ai_err:
                self.logger.error("AI-сервис упал: %s", ai_err)
                answer = None

            # 2) Если пусто — ручной выбор
            if not answer:
                self.logger.warning("AI не выбрал ни одного МВД — переходим на ручной выбор")

            else:
                clicked = self.main.select_mvd(answer)
                if clicked:
                    self.logger.warning("Выбран МВД: %s", answer)
                else:
                    self.logger.error(
                        "Не удалось автоматически кликнуть по «%s» — перейдите к ручному выбору", 
                        answer
                    )
                    
            self.main.phone_input(self.phone_number)

            self.main.input_email(self.email)

            self.main.input_post()

            locality = self.file_service.get_locality(self.root_folder)

            self.main.input_fio(locality,self.bd)

            self.main.text_input(get_text(locality, fio, birthday, self.bd))

            try:
                self.main.input_files(found)
            except Exception as e:
                self.logger.warning(f'Внимание! Какой то из файлов не был загружен!')

            try:
                self.main.check_len_files()
            except FileNotFoundError:
                self.logger.warning(f'Проблема при загрузке файлов! Проверь их количество!')
                self._pause("Проверь все ли файлы загружены и нажми «Продолжить». Если файлов не хватает - загрузи вручную")


            self.logger.warning('Обхожу капчу, ожидай.')

            try:
                capthca_path = self.main.captcha_src()
            except:
                self.logger.error('Ошибка при прокрутке и скриншота капчи!')

            self.main.input_captcha(self.captcha_service.solve(capthca_path))

            self._pause("Проверь правильность введенных данных и нажми «Продолжить».")

            self.main.accept_the_application()

            MAX_RETRIES = 3
            for attempt in range(1, MAX_RETRIES + 1):
                try:
                    # пытаемся нажать подтверждение кода из письма
                    self.final.email_complete_btn()
                except TimeoutException as e:
                    self.logger.warning("Капча не принята (попытка %d): %s", attempt, e)
                    # снимаем новый скрин
                    captcha_path = self.main.captcha_src()
                    captcha_text = self.captcha_service.solve(captcha_path)
                    if not captcha_text:
                        self.logger.error("Сервис не вернул текст капчи")
                        break

                    # вводим новый код
                    self.main.input_captcha(captcha_text)
                    # ждем, может, секунду, чтобы капча «подхватилась»
                    time.sleep(1)
                    # снова кликаем «Отправить»
                    self.main.accept_the_application()
                    # и loop повторится: в начале попробуем email_complete_btn()
                else:
                    self.logger.info("Капча успешно решена на попытке %d", attempt)
                    break
            else:
                # после трёх неудач — просим юзера
                self._pause("Капчу решить не удалось, ПРОСТО впиши ее в поле и нажми «Продолжить».")
                self.main.accept_the_application()
                self.final.email_complete_btn()

            try:
                time.sleep(2)
                email_code = self.mail.get_code()
                if email_code is None:
                    raise ValueError("Письмо с кодом не найдено")
            except Exception as e:
                self.logger.error(f"Код с почты не получен: {e}")
                email_code = self._pause("Проблема с почтой. Возможно нужно будет ввести код вручную. Нажми «Продолжить».")

            self.logger.info(f'Код проверки {email_code}')
            self.final.input_email_code(email_code)

            self.final.complete_email()

            self.final.final_checkbox_click()

            err_text = self.final.wait_for_error()
            if err_text:
                self.logger.error(f"Код неверен: «{err_text}»")
                self.logger.info(f"Введенный код неверен!")
                # тут можете повторить ввод или прервать, как вам нужно
            else:
                self.logger.info("Код принят, продолжаем дальше")

            self._pause("ПРОВЕРЬ ВСЕ ДАННЫЕ, ЗАЯВЛЕНИЕ УЙДЕТ ПОСЛЕ КНОПКИ «Продолжить».")

            
            self.final.send_an_application()

            try:
                link = self.final.get_link()
                self._pause("Проставь комментарий и нажми «Продолжить» для следующего договора.")
            except:
                self.logger.warning('Неудалось получить ссылку! Скопируй самостоятельно и вставь комментарий')
                self._pause("Проставь комментарий и нажми «Продолжить» для следующего договора.")
            try:
                self.logger.warning('Записываю в ексельку')
                self.report_excel.add_link(fio, loan_id, link)
                
            except Exception as e_excel:
                self.logger.error(f'Я не смог записать в эксель {e_excel}')
            end_time = time.time()
            self.logger.info(f'Время обработки {end_time - start_time}')
            self.file_service.move_folder(folder_path, self.dst_root)
