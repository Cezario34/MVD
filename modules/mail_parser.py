import imaplib
import email
import re
from typing import Optional

class MailCode:
    def __init__(
        self,
        login: str,
        password: str,
        server: str,
        port: int,
        sender: str,
        folder: str = "INBOX",
    ):
        self.login    = login
        self.password = password
        self.server   = server
        self.port     = port
        self.sender   = sender
        self.folder   = folder

    def _connect(self):
        m = imaplib.IMAP4_SSL(self.server, self.port)
        m.login(self.login, self.password)
        m.select(self.folder)
        return m

    def get_email(self, subject: Optional[str] = None) -> Optional[str]:
        """
        Возвращает body (HTML или plain) последнего письма
        от self.sender (и с темой subject, если указана).
        """
        try:
            m = self._connect()

            # Формируем критерии поиска
            criteria = [f'FROM "{self.sender}"']
            if subject:
                criteria.append(f'SUBJECT "{subject}"')
            # IMAP требует, чтобы все критерии были в одном аргументе, разделённые пробелом
            search_str = " ".join(criteria)

            status, data = m.search(None, search_str)
            if status != "OK":
                print("Ошибка при поиске писем:", status)
                m.logout()
                return None

            ids = data[0].split()
            if not ids:
                print("Нет писем от этого отправителя/с темой.")
                m.logout()
                return None

            # Возьмём последнее письмо
            latest_id = ids[-1]

            # Забираем весь месcедж
            status, msg_data = m.fetch(latest_id, "(RFC822)")
            if status != "OK":
                print("Не удалось получить тело письма")
                m.logout()
                return None

            raw = msg_data[0][1]  # байты
            msg = email.message_from_bytes(raw)

            # Ищем HTML или plain
            body = None
            if msg.is_multipart():
                for part in msg.walk():
                    ctype = part.get_content_type()
                    disp  = str(part.get("Content-Disposition"))
                    if ctype == "text/html" and "attachment" not in disp:
                        body = part.get_payload(decode=True).decode(part.get_content_charset() or "utf-8", errors="replace")
                        break
                else:
                    # fallback to text/plain
                    part = msg.get_payload(0)
                    body = part.get_payload(decode=True).decode(part.get_content_charset() or "utf-8", errors="replace")
            else:
                body = msg.get_payload(decode=True).decode(msg.get_content_charset() or "utf-8", errors="replace")

            m.logout()
            return body

        except Exception as e:
            print("Ошибка при работе с почтой:", e)
            return None

    def get_code(self, subject: Optional[str] = None) -> Optional[str]:
        """
        Ищет в теле письма кусок вида:
            Ваш код:</h2><h1><em>CODE</em>
        и возвращает CODE.
        """
        body = self.get_email(subject)
        if not body:
            print("Письмо не найдено")
            return None

        match = re.search(
            r'Ваш код:</h2>\s*<h1><em[^>]*>([\w\dА-Яа-я]+)</em>',
            body,
            re.IGNORECASE | re.DOTALL
        )
        if match:
            return match.group(1)
        else:
            print("Код не найден в письме")
            return None
        
