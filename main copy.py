import logging

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

from modules.paths import build_paths, ensure_dirs_exist
from log_filters import ErrorLogFilter, CriticalLogFilter, DebugWarningLogFilter
from modules.processor import LoanProcessor


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
    root_folder = r'\\Pczaitenov\159\Ежедневная подача\Галимзянова\14.06.2025 дк'
    dst_root = build_paths(
        base_share=r"\\Pczaitenov\159\Ежедневная подача\Галимзянова",
        loan_type="дк"
    )
    ensure_dirs_exist(root_folder, dst_root)
    keywords = [".docx", ".xlsx", ".pdf", ".docx.doc"]
    driver_kwargs = get_driver_kwargs()
    proc = LoanProcessor(root_folder, dst_root, keywords, driver_kwargs)
    proc.run()
