from selenium.common.exceptions import WebDriverException, TimeoutException, InvalidArgumentException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class WelcomePage:

    def __init__(self,
                driver, 
                logger):
                
        self.driver = driver
        self.short_wait = WebDriverWait(driver, 150)
        self.long_wait = WebDriverWait(driver, 60)
        self.logger = logger

    def open(self, region_code: int):
        url = f"https://{region_code}.xn--b1aew.xn--p1ai/request_main"
        try:
            self.driver.get(url)
        except (WebDriverException, TimeoutException, InvalidArgumentException):
            raise TimeoutException

        if "/503.jpg" in self.driver.page_source.lower():                    
            raise WebDriverException

    def click_statement_checkbox(self):
        """Клик по чекбоксу гражданина"""
        self.logger.info('Кликаю по заявлению от гражданина')
        checkbox_label2 = self.long_wait.until(
            EC.element_to_be_clickable((By.CLASS_NAME, "checkbox"))
            )
        checkbox_label2.click()

    def click_statement_button(self):
        """Клик по кнопке подать заявление"""
        button = self.short_wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Подать обращение от гражданина')]")))
        button.click()
        self.short_wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "modal-content")))
    
    def click_gos_service(self):
        """Клик по всплывающему окну войти через госуслуги"""
        btn_gos_uslugi = self.short_wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[.//img[@alt='Войти через Госуслуги']]"))
        )
        btn_gos_uslugi.click()
        # qr_click

    def gos_auth_page():
        self.click_statement_checkbox()
        self.click_statement_button()