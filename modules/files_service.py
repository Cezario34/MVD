import os
import shutil
import glob
import uuid
import logging
from typing import List, Tuple, Optional


class FileService:


    def __init__(self, temp_dir:str,
                 extensions: List[str],
                 logger: Optional[logging.Logger] = None):
        
        self.temp_dir = temp_dir
        self.extensions = extensions
        self.logger = logger or logging.getLogger(__name__)

    
    def to_long_path(self, path: str) -> str:
        if path.startswith(r"\\?\UNC") or path.startswith(r"\\?\\") or path.startswith(r"\\?\\"):
            return path
        if path.startswith(r"\\"):
            return r"\\?\UNC" + path[1:]
        return r"\\?\\" + os.path.abspath(path)
    
    def extract_number_before_dash(self, name: str) -> int:
        try:
            return int(name.split("-")[0])
        except (IndexError, ValueError):
            return float('inf')
        
    def find_first_subfolder(self, root_folder: str) -> Optional[str]:
        entries = os.listdir(root_folder)
        candidates = [
            d for d in entries
            if os.path.isdir(os.path.join(root_folder, d))
        ]
        if not candidates:
            return None
        candidates.sort(key=self.extract_number_before_dash)
        first = candidates[0]
        full = os.path.join(root_folder, first)
        self.logger.debug(f"Первая подпапка: {full}")
        return full
    
    def prepare_for_upload(self, original_path: str) -> Optional[str]:
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir, exist_ok=True)

        src = self.to_long_path(original_path)
        name = os.path.basename(src)
        short = f"{uuid.uuid4().hex[:6]}_{name}"
        dst   = os.path.join(self.temp_dir, short)
        try:
            shutil.copy2(src, dst)
            self.logger.debug(f"Скопировано для загрузки: {dst}")
            return dst
        except Exception as e:
            self.logger.error(f"Не удалось скопировать {src}: {e}")
            return None

    def find_files_by_keywords(
        self,
        root_folder: str
    ) -> Tuple[List[str], Optional[str]]:
        """
        Возвращает (список путей к безопасным копиям, путь к самой папке-источнику).
        """
        source_folder = self.find_first_subfolder(root_folder)
        if source_folder is None:
            self.logger.error("Не найдена ни одна подпапка в %s", root_folder)
            return [], None

        found = []
        self.logger.info(f"Ищем файлы {self.extensions} в {source_folder}")
        for fname in os.listdir(source_folder):
            full = os.path.join(source_folder, fname)
            long_full = self.to_long_path(full)
            if not os.path.isfile(long_full):
                continue
            ext = os.path.splitext(fname)[1].lower()
            if ext in self.extensions:
                safe = self.prepare_for_upload(full)
                if safe:
                    found.append(safe)

        return found, source_folder
    
    
    def move_folder(self, src_folder: str, dst_root: str) -> str:
        if not os.path.isdir(src_folder):
            raise ValueError(f"Исходная папка не найдена: {src_folder}")
        if not os.path.isdir(dst_root):
            raise ValueError(f"Целевая папка не найдена: {dst_root}")

        dst_folder = os.path.join(dst_root, os.path.basename(src_folder))
        if os.path.exists(dst_folder):
            raise FileExistsError(f"Папка {dst_folder} уже существует!")

        shutil.move(src_folder, dst_root)
        self.logger.info("Перемещено %s → %s", src_folder, dst_root)
        return dst_folder
    

    def cleanup_temp_uploads(self):
        pattern = os.path.join(self.temp_dir, "*")
        for f in glob.glob(pattern):
            try:
                os.remove(f)
            except:
                pass
        self.logger.debug("Очистил temp-папку %s", self.temp_dir)


    def get_loan_id(self, root_folder: str) -> Optional[str]:
        first = self.find_first_subfolder(root_folder)
        return first.split("_")[1] if first else None


    def get_locality(self, root_folder: str) -> Optional[str]:
        first = self.find_first_subfolder(root_folder)
        # пример логики — может потребовать правки под ваши реальныe имена
        return first.split()[2].split("\\")[1] if first else None