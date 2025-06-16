import os
import shutil
from typing import List, Tuple



def extract_number_before_dash(name: str) -> int:
    try:
        return int(name.split("-")[0])
    except (IndexError, ValueError):
        return float('inf')  # если имя не по формату — в конец


def find_first_subfolder(root_folder: str) -> str:
    """
    Возвращает путь к первой подпапке внутри root_folder,
    отсортированной по числу перед первым тире.
    """
    subfolders = [
        entry for entry in os.listdir(root_folder)
        if os.path.isdir(os.path.join(root_folder, entry))
    ]

    sorted_folders = sorted(subfolders, key=extract_number_before_dash)

    if sorted_folders:
        return os.path.join(root_folder, sorted_folders[0])
    return None

def find_files_by_keywords(folder_path: str, keywords: list) -> Tuple[list[str], str]:
    folder_path = find_first_subfolder(folder_path)

    found = []
    for fname in os.listdir(folder_path):
        full_path = os.path.join(folder_path, fname)
        if not os.path.isfile(full_path):
            continue
        for kw in keywords:
            if kw.lower() in fname.lower():
                found.append(full_path)
                break

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


