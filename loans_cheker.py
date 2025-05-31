import os
import shutil

root_folder = r"C:\Users\1\Desktop\Сделать"
dst_root = r"C:\Users\1\Desktop\Готовые 3105"
keywords = ["День2", "Договор", "comeback", "подтверждение", "справка"]  # твои ключевые слова


def find_first_subfolder(root_folder):
    """
    Возвращает путь к первой подпапке внутри root_folder.
    """
    for entry in sorted(os.listdir(root_folder)):
        full_path = os.path.join(root_folder, entry)
        if os.path.isdir(full_path):
            return full_path
    return None

def find_files_by_keywords(folder_path, keywords, dst_root):


    """
    Ищет файлы, имя которых содержит одно из ключевых слов.
    :param folder_path: папка для поиска
    :param keywords: список подстрок (ключевых слов) для поиска в имени файла
    :return: список путей к найденным файлам
    """
    folder_path = find_first_subfolder(root_folder)

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


def move_folder(src_folder, dst_root):
    """
    Перемещает папку src_folder в папку dst_root (если уже есть — ошибка).
    :param src_folder: полный путь к исходной подпапке
    :param dst_root: полный путь к целевой папке (туда перемещаем)
    :return: полный путь, по которому теперь находится папка
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

found = find_files_by_keywords(root_folder, keywords, dst_root)
for i in found:
    print(i)