import logging
import sys
from log_filters import ErrorLogFilter, CriticalLogFilter, DebugWarningLogFilter



from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

from modules.paths import build_paths, ensure_dirs_exist
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
import undetected_chromedriver as uc
from interface import App

root = logging.getLogger()           # <- именно root
root.setLevel(logging.DEBUG)

console = logging.StreamHandler(sys.stdout)
console.setLevel(logging.INFO)
console.addFilter(DebugWarningLogFilter())
console.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
root.addHandler(console)

err_fh = logging.FileHandler("error.log", mode="w", encoding="utf-8")
err_fh.setLevel(logging.ERROR)
err_fh.addFilter(ErrorLogFilter())
err_fh.setFormatter(logging.Formatter(
    "[%(asctime)s] %(levelname)-8s %(name)s:%(lineno)d - %(message)s"
))
root.addHandler(err_fh)


crit_fh = logging.FileHandler("critical.log", mode="w", encoding="utf-8")
crit_fh.setLevel(logging.CRITICAL)
crit_fh.addFilter(CriticalLogFilter())
crit_fh.setFormatter(err_fh.formatter)
root.addHandler(crit_fh)


def get_driver_kwargs() -> dict:
    opts = uc.ChromeOptions()
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

    file_svc = FileService(
        temp_dir   = r"C:\Temp\SeleniumUploads",
        extensions = [".docx", ".xlsx", ".pdf", ".docx.doc"],
        logger     = logging.getLogger("files")
    )


    mail_service = MailCode(
        login   = cfg.email.email_user,
        password = cfg.email.email_pass,
        server   = cfg.email.imap_server,
        port     = cfg.email.imap_port,
        sender   = cfg.email.sender_email,
    )
    report_excel = ReportService(logging.getLogger("report"))

    captcha = CaptchaService(api_key=cfg.captcha.api_key)
    mvd = MvdService(cfg.maps.api_key,
            keywords=["отдел полиции", "оп", "отделение полиции", "омвд"]
    )
    driver_kwargs = get_driver_kwargs()

    ai_svc = AIService(api_key=cfg.ai.api_key)

    bd = 'ps'        
    proc = LoanProcessor(root_folder="", dst_root="", unfulfilled_root="",
                         keywords= file_svc.extensions, 
                         captcha_service=captcha, 
                         driver_kwargs=driver_kwargs,
                         file_service = file_svc,
                         report_excel = report_excel,
                         mvd = mvd,
                         db_service = db_svc,
                         mail = mail_service,
                         ai_answer=ai_svc,
                         bd = bd)
    
    app = App(processor=proc)
    proc._on_pause = app.show_pause_prompt  
    app.mainloop()
    