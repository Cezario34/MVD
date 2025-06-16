from dataclasses import dataclass
from environs import Env




env = Env()
env.read_env()  # <-- путь указываем здесь!



@dataclass
class DatabaseConfig:
    dbname: str
    user: str
    password: str
    host: str
    port: str



    def get_conn_string(self) -> str:
        return (
        f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.dbname}"
    )


@dataclass
class EmailConfig:
    imap_server: str 
    email_user: str  
    email_pass: str 
    imap_port: int 
    sender_email: str


@dataclass
class GosUslugiConfig:
    login: str
    password: str


@dataclass
class mainDBConfig:
    ps: str
    dk: str


@dataclass
class PersonData:
    login: str
    password: str
    email: str

dbConfig = DatabaseConfig(
    dbname=env('dbname'),
    user=env('user'),
    password=env('password'),
    host=env('host'),
    port=env('port'),

)


conn_string = dbConfig.get_conn_string()


main_db_config = mainDBConfig(
    ps = env('ps'),
    dk = env('dk')
)


person = PersonData(
    login= env('LOGIN'),
    password= env('PASSWORD_pers'),
    email=env('EMAIL')

)


email_auth = EmailConfig(
    imap_server = env('imap_server'),
    email_user = env('email_user'),
    email_pass = env('email_pass'),
    imap_port = env('imap_port'),
    sender_email = env('sender_email')
)

