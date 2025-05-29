import imaplib
import email
import os
import sys  


imap_server = 'imap.yandex.ru'  # IMAP-сервер
email_user = 'v.gluhov@cyberbird.tech'  # Ваш логин
email_pass = 'zxeyypwdykrhgvof'  # Ваш пароль
imap_port = 993  # Порт IMAP

sender_email = 'info@calendar.yandex.ru'  # <- От кого ищем письмо


try:
    # Подключение к серверу
    mail = imaplib.IMAP4_SSL(imap_server, imap_port)
    mail.login(email_user, email_pass)
    mail.select('inbox')

    # Поиск писем от нужного отправителя
    status, messages = mail.search(None, f'(FROM "{sender_email}")')
    mail_ids = messages[0].split()

    if not mail_ids:
        print('Нет писем от этого отправителя.')
    else:
        # Берём самое последнее письмо
        last_id = mail_ids[-1]
        status, msg_data = mail.fetch(last_id, '(RFC822)')
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])

                # Извлекаем тело письма
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8')
                            break
                else:
                    body = msg.get_payload(decode=True).decode(msg.get_content_charset() or 'utf-8')

                print('Тело письма:')
                print(body)
                # Теперь body – это переменная с текстом письма

    mail.logout()
except Exception as e:
    print(f"Ошибка: {e}")