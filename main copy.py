import logging
import sys

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

from modules.paths import build_paths, ensure_dirs_exist
from log_filters import ErrorLogFilter, CriticalLogFilter, DebugWarningLogFilter
from modules.processor import LoanProcessor
from modules.captcha_service import CaptchaService
import modules.config_data as config_data
from modules.ai_service import AIService
from modules.files_service import FileService
from modules.report_service import ReportService
from modules.mvd_service import MvdService
from modules.db_service import LoanDataService
from modules.config_data import load_config
from modules.mail_parser import MailCode

def configure_logging():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    formatter_1 = logging.Formatter(
        fmt='[%(asctime)s] #%(levelname)-8s %(filename)s:'
            '%(lineno)d - %(name)s:%(funcName)s - %(message)s'
    )

    formatter_2 = logging.Formatter(
        fmt='[%(asctime)s] #%(levelname)-8s - %(message)s'
    )

    error_file = logging.FileHandler('error.log', 'w', encoding='utf-8')
    error_file.setLevel(logging.DEBUG)
    error_file.addFilter(ErrorLogFilter())
    error_file.setFormatter(formatter_1)

    stdout = logging.StreamHandler(sys.stdout)
    stdout.addFilter(DebugWarningLogFilter())
    stdout.setFormatter(formatter_2)

    stderr = logging.StreamHandler()
    critical_file = logging.FileHandler('critical.log', mode='w', encoding='utf-8')
    critical_file.setFormatter(fmt=formatter_1)
    critical_file.addFilter(CriticalLogFilter())

    logger.addHandler(stderr)
    logger.addHandler(critical_file)
    logger.addHandler(stdout)
    logger.addHandler(error_file)


def get_driver_kwargs() -> dict:
    configure_logging()
    opts = Options()
    opts.add_argument("--window-size=1200,800")
    opts.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    return {
        "service": ChromeService(ChromeDriverManager().install()),
        "options": opts}


if __name__ == '__main__':

    cfg = load_config(r"\\Pczaitenov\159\Служебная папка\.env")

    db_svc = LoanDataService(
        engine_conn_string=cfg.database.get_conn_string(),
        remote_db_map = {
            "ps": cfg.main_db.ps,
            "dk": cfg.main_db.dk
        },
        logger = logging.getLogger("db")
    )

    root_folder = r'\\Pczaitenov\159\Ежедневная подача\Галимзянова\14.06.2025 дк'
    dst_root, unfulfilled_root = build_paths(
        base_share=r"\\Pczaitenov\159\Ежедневная подача\Галимзянова",
        loan_type="ПС")
    ensure_dirs_exist(unfulfilled_root, dst_root)


    file_svc = FileService(
        temp_dir   = r"C:\Temp\SeleniumUploads",
        extensions = [".docx", ".xlsx", ".pdf", ".docx.doc"],
        logger     = logging.getLogger("files")
    )

    mail_code = (cfg.email.email_user, cfg.email.email_pass,
                 cfg.email.imap_server, cfg.email.imap_port, cfg.email.sender_email)

    report_excel = ReportService(logging.getLogger("report"))

    captcha = CaptchaService(api_key=cfg.captcha.api_key)
    mvd = MvdService(cfg.yandexMaps.api_key,
            keywords=["отдел полиции", "оп", "отделение полиции", "омвд"]
    )
    driver_kwargs = get_driver_kwargs()

    ai_svc = AIService(api_key=cfg.ai.api_key)

    proc = LoanProcessor(root_folder=root_folder, dst_root=dst_root, unfulfilled_root=unfulfilled_root,
                         keywords= file_svc.extensions, 
                         captcha_service=captcha, 
                         driver_kwargs=driver_kwargs,
                         file_service = file_svc,
                         report_excel = report_excel,
                         mvd = mvd,
                         db_service = db_svc,
                         mail = mail_code,
                         ai_answer=ai_svc)
    proc.run()
