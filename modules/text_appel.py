
def get_text(locality: str, fio: str, birthday: str, bd: str, reg_address: str) -> str:
    return f"""Прошу Вас рассмотреть заявление {locality}{bd} о возбуждении уголовного дела в отношении {fio} {birthday} 
года рождения, зарегистрированного(-ой) по адресу: {reg_address}
"""