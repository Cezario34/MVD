from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

from modules.paths import build_paths, ensure_dirs_exist
from modules.processor import LoanProcessor


def get_driver_kwargs() -> dict:
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
