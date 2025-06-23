from selenium.common.exceptions import WebDriverException,ElementNotVisibleException, TimeoutException, InvalidArgumentException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class FinalPage():

    def __init__(self, driver, logger, wait):

        self.driver = driver
        self.logger = logger
        self.wait = WebDriverWait(driver, 10)
    
    def email_complete_btn(self):
        self.wait.until(
                EC.element_to_be_clickable((By.ID, "confirm_but"))
            ).click()

    def input_email_code(self,code):
        email_code_input = self.wait.until(
                EC.visibility_of_element_located((By.CLASS_NAME, "confirm-mail"))
            )
        email_code_input.send_keys(code)

    def complete_email(self):
        button_confirm_email = self.driver.find_element(By.ID, "confirm_mail").click()

    
    def final_checkbox_click(self):
        checkbox = self.driver.find_element(By.ID, 'correct')

        self.driver.execute_script("arguments[0].click();", checkbox)


    def send_an_application(self):
        button = self.wait.until(
                    EC.element_to_be_clickable((By.ID, "form-submit"))
                )
        self.driver.execute_script("arguments[0].click();", button)


    def get_link(self):
        try:
            p_code = self.driver.find_element(By.XPATH, "//p[contains(text(), 'Код проверки статуса обращения')]")
            status_code = p_code.find_element(By.TAG_NAME, "b").text.strip()
            return status_code
        except:
            raise ElementNotVisibleException

    def wait_for_error(self) -> str:
        """
        Ждём появления <span class="error">,
        возвращаем его текст или пустую строку, если не появилось.
        """
        try:
            err_elem = self.wait.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "span.error"))
            )
            return err_elem.text.strip()
        except TimeoutException:
            raise ""
