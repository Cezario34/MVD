import pandas as pd
import logging
from pathlib import Path



class ReportService:

    def __init__(self, logger: logging.Logger = None):
        self.logger = logger or logging.getLogger(__name__)
        self.file_path = (
    r"\\Pczaitenov\159\Ежедневная подача\Галимзянова\Выполненные\Отчетность МВД.xlsx"
    )       

    def add_link(self, loan_id: str, link: str) -> None:

        try:
            df= pd.read_excel(self.file_path)
        except Exception as e:
            self.logger.error("Не удалось прочитать отчёт %s: %s", self.file_path, e)
            raise
        
        new_row = pd.DataFrame({'loan_id': [loan_id], 'link': [link]})
        df = pd.concat([df, new_row], ignore_index=True, axis=0)

        try:
            df.to_excel(self.file_path, index=False)
            self.logger.info("В отчёт %s добавлена строка: %s → %s",
                                self.file_path.name, loan_id, link)
        except Exception as e:
            self.logger.error("Не удалось записать отчёт %s: %s", self.file_path, e)
            raise
