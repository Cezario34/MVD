

#Блок  авторизации гос услуг
# try:
#     time.sleep(3)
#     inputs = driver.find_elements(By.TAG_NAME, "input")
#     for inp in inputs:
#         print(inp.get_attribute("outerHTML"))

#     login_input = wait.until(
#         EC.visibility_of_element_located((By.ID, "login"))
#     )
#     login_gos = input('Введи логин гос услуг')
#     # login_input.send_keys(person.login)
#     login_input.send_keys(login_gos)
#     password_input_gos = input('Введи пароль гос услуг')
#     password_input = wait.until(
#         EC.visibility_of_element_located((By.ID, "password"))
#     )
#     password_input.send_keys(password_input_gos)
#     # password_input.send_keys(person.password)
#     login_button = wait.until(
#         EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Войти')]"))
#     )
#     login_button.click()
#     time.sleep(3)
#     # short_code=input('Вставьте 6 код\n')
#     # code_input = wait.until(
#     #     EC.visibility_of_element_located((By.CSS_SELECTOR, "esia-code-input input"))
#     # )
#     # code_input.send_keys(short_code)
# except TimeoutException:
#     logging.info('Авторизация не требуется')