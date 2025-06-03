import imaplib
import email
import os
import sys  
import re
from config_data import email_auth



def get_email(subject: str) -> str | None:
    try:
        # Подключение к серверу
        mail = imaplib.IMAP4_SSL(email_auth.imap_server, email_auth.imap_port)
        mail.login(email_auth.email_user, email_auth.email_pass)
        mail.select('inbox')

        # Поиск писем только от нужного отправителя
        status, messages = mail.search(None, f'(FROM "{email_auth.sender_email}")')
        mail_ids = messages[0].split()
        if not mail_ids:
            print('Нет писем от этого отправителя.')
            mail.logout()
            return None

        # Перебор писем от новых к старым
        for mail_id in reversed(mail_ids):
            status, msg_data = mail.fetch(mail_id, '(RFC822)')
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    # Проверяем тему письма (полное совпадение)
                    subj = email.header.decode_header(msg["Subject"])[0]
                    subj_text = subj[0]
                    if isinstance(subj_text, bytes):
                        subj_text = subj_text.decode(subj[1] or "utf-8")
                    if subj_text.strip() != subject.strip():
                        continue  # тема не совпадает — пропускаем

                    # Парсим тело письма (plain → html)
                    body = None
                    if msg.is_multipart():
                        for part in msg.walk():
                            ctype = part.get_content_type()
                            cdispo = part.get_content_disposition()
                            if ctype == "text/plain" and cdispo != "attachment":
                                body = part.get_payload(decode=True).decode(part.get_content_charset() or "utf-8")
                                break
                        if not body:
                            for part in msg.walk():
                                ctype = part.get_content_type()
                                cdispo = part.get_content_disposition()
                                if ctype == "text/html" and cdispo != "attachment":
                                    body = part.get_payload(decode=True).decode(part.get_content_charset() or "utf-8")
                                    break
                    else:
                        ctype = msg.get_content_type()
                        if ctype == "text/plain":
                            body = msg.get_payload(decode=True).decode(msg.get_content_charset() or "utf-8")
                        elif ctype == "text/html":
                            body = msg.get_payload(decode=True).decode(msg.get_content_charset() or "utf-8")

                    mail.logout()
                    return body  # возвращаем тело первого найденного письма с нужной темой

        print('Нет писем с такой темой от этого отправителя.')
        mail.logout()
        return None
    except Exception as e:
        print(f"Ошибка: {e}")
        return None

def get_code() -> str | None:
    email_body = get_email("Проверка почты")
    if not email_body:
        print("Письмо не найдено")
        return None

    match = re.search(
        r'Ваш код:</h2>\s*<h1><em[^>]*>([\w\dА-Яа-я]+)</em>',
        email_body,
        re.IGNORECASE | re.DOTALL
    )

    if match:
        code = match.group(1)
        return code
    else:
        print("Код не найден")
        return None


if __name__ == ('__main__'):
    get_code()