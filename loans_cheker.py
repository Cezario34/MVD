import os
import shutil
import glob
import uuid
from typing import List, Tuple

TEMP_UPLOAD_DIR = r"C:\Temp\SeleniumUploads"

def to_long_path(path: str) -> str:
    if path.startswith(r"\\?\UNC") or path.startswith(r"\\?\\") or path.startswith("\\?\\"):
        return path  # уже длинный путь
    if path.startswith(r"\\"):
        return r"\\?\UNC" + path[1:]
    return r"\\?\\" + os.path.abspath(path)

def extract_number_before_dash(name: str) -> int:
    try:
        return int(name.split("-")[0])
    except (IndexError, ValueError):
        return float('inf')

def find_first_subfolder(root_folder: str) -> str:
    subfolders = [
        entry for entry in os.listdir(root_folder)
        if os.path.isdir(os.path.join(root_folder, entry))
    ]
    sorted_folders = sorted(subfolders, key=extract_number_before_dash)

    if sorted_folders:
        selected = os.path.join(root_folder, sorted_folders[0])
        return selected
    return None

def prepare_for_upload(long_path: str, temp_dir: str = TEMP_UPLOAD_DIR) -> str:
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    long_path = to_long_path(long_path)
    filename = os.path.basename(long_path)
    short_name = f"{uuid.uuid4().hex[:6]}_{filename}"
    short_path = os.path.join(temp_dir, short_name)

    try:
        shutil.copy2(long_path, short_path)
        return short_path
    except Exception as e:
        print(f"[ERROR] Не удалось скопировать {long_path}: {e}")
        return None

def find_files_by_keywords(folder_path: str, extensions: list[str]) -> Tuple[list[str], str]:
    folder_path = find_first_subfolder(folder_path)
    if not folder_path:
        print("[ERROR] Не найдена ни одна подпапка.")
        return None

    found = []
    print(f"[DEBUG] Поиск в папке: {folder_path}")
    for fname in os.listdir(folder_path):
        full_path = os.path.join(folder_path, fname)
        # Проверяем файл с учётом длинных путей
        long_full_path = to_long_path(full_path)
        if not os.path.isfile(long_full_path):
            continue

        ext = os.path.splitext(fname)[1].lower()
        if ext in extensions:
            safe_path = prepare_for_upload(full_path)
            if safe_path:
                found.append(safe_path)

    return found, folder_path

def move_folder(src_folder: str, dst_root: str) -> str:
    """
    Перемещает папку src_folder в папку dst_root (если уже есть — ошибка).
    """
    if not os.path.isdir(src_folder):
        raise ValueError(f"Исходная папка не найдена: {src_folder}")
    if not os.path.isdir(dst_root):
        raise ValueError(f"Целевая папка не найдена: {dst_root}")
    dst_folder = os.path.join(dst_root, os.path.basename(src_folder))
    if os.path.exists(dst_folder):
        raise FileExistsError(f"Папка {dst_folder} уже существует!")
    shutil.move(src_folder, dst_root)
    return dst_folder


def get_loan_id(path) -> str:
    return find_first_subfolder(path).split('_')[1]


def get_Locality(path) -> str:
    return find_first_subfolder(path).split()[2].split('\\')[1]


def cleanup_temp_uploads(temp_dir: str = TEMP_UPLOAD_DIR):
    for f in glob.glob(os.path.join(temp_dir, "*")):
        os.remove(f)

extensions = [".docx", ".xlsx", ".pdf", ".docx.doc"]

