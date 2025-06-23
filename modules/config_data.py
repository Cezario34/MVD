import os
from dataclasses import dataclass
from environs import Env
from typing import Optional


@dataclass
class DatabaseConfig:
    dbname: str
    user: str
    password: str
    host: str
    port: int

    def get_conn_string(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.dbname}"


@dataclass
class EmailConfig:
    imap_server: str
    email_user: str
    email_pass: str
    imap_port: int
    sender_email: str


@dataclass
# class GosUslugiConfig:
#     login: str
#     password: str


@dataclass
class MainDBConfig:
    ps: str
    dk: str


@dataclass
class PersonData:
    login: str
    password: str
    email: str


@dataclass
class CaptchaConfig:
    api_key: str
    http_proxy: Optional[str] = None
    https_proxy: Optional[str] = None


@dataclass
class YandexMaps:
    api_key: str

@dataclass
class AIConfig:
    api_key: str


@dataclass
class AppConfig:
    database      : DatabaseConfig
    email         : EmailConfig
    main_db       : MainDBConfig
    person        : PersonData
    captcha       : CaptchaConfig
    ai            : AIConfig
    maps          : YandexMaps


def load_config(env_path: Optional[str] = None) -> AppConfig:
    """
    Читает .env (по умолчанию из фиксированного пути или текущей папки)
    и возвращает единый AppConfig со всеми секциями.
    """
    # 1) Создаём парсер
    env = Env()
    if env_path:
        env.read_env(env_path, override=True)
    else:
        # по умолчанию ищем .env в корне проекта  
        env.read_env()

    # 2) Собираем по секциям
    db_cfg = DatabaseConfig(
        dbname   = env("DB_NAME"),
        user     = env("DB_USER"),
        password = env("DB_PASS"),
        host     = env("DB_HOST"),
        port     = env.int("DB_PORT"),
    )

    email_cfg = EmailConfig(
        imap_server = env("IMAP_SERVER"),
        email_user  = env("EMAIL_USER"),
        email_pass  = env("EMAIL_PASS"),
        imap_port   = env.int("IMAP_PORT"),
        sender_email= env("SENDER_EMAIL"),
    )

    main_db_cfg = MainDBConfig(
        ps = env("PS_CONN"),
        dk = env("DK_CONN"),
    )

    person = PersonData(
        login    = env("LOGIN"),
        password = env("PASSWORD_PERS"),
        email    = env("EMAIL"),
    )

    captcha_cfg = CaptchaConfig(
        api_key    = env("API_CAPTCHA"),
        http_proxy = env("HTTP_PROXY", None),
        https_proxy= env("HTTPS_PROXY", None),
    )

    ai_cfg = AIConfig(
        api_key = env("API_KEY"),
    )

    maps_cfg = YandexMaps(
        api_key = env("API_YANDEX")
    )

    # 3) Объединяем
    return AppConfig(
        database  = db_cfg,
        email     = email_cfg,
        main_db   = main_db_cfg,
        person    = person,
        captcha   = captcha_cfg,
        ai        = ai_cfg,
        maps      = maps_cfg
    )