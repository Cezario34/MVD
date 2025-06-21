import os
from datetime import date

def current_date_str() -> str:
    """
    Возвращает сегодняшнюю дату в формате 'DD.MM.YYYY'.
    """
    return date.today().strftime("%d.%m.%Y")

def build_paths(
    base_share: str,
    loan_type: str
) -> tuple[str, str, str]:

    today = current_date_str()

    dst_root         = os.path.join(base_share, "Выполненные", today, loan_type)
    unfulfilled_root = os.path.join(base_share, "Невыполненные", today, loan_type)

    return dst_root, unfulfilled_root

def ensure_dirs_exist(*paths: str) -> None:
    """
    Создаёт все переданные папки (если их ещё нет).
    """
    for p in paths:
        os.makedirs(p, exist_ok=True)