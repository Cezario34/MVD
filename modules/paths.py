import os
from datetime import date
# from typing import Tuple


def get_date_str(fmt: str = "%d.%m.%Y") -> str:
    return date.today().strftime(fmt)


def build_paths(base_share: str, loan_type: str, date_str: str = None) -> str:

    if date_str is None:
        date_str = get_date_str()

    # root_folder = os.path.join(base_share, date_str, loan_type)
    dst_root = os.path.join(base_share, "Выполненные", date_str, loan_type)
    unfulfilled_root = os.path.join(base_share, "Невыполненные", date_str, loan_type)
    return dst_root, unfulfilled_root


def ensure_dirs_exist(*paths: str) -> None:
    for p in paths:
        os.makedirs(p, exist_ok=True)


print(build_paths('\\Pczaitenov\159\Ежедневная подача\Галимзянова',"ПС"))