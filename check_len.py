import os
import shutil

def to_long_path(path: str) -> str:
    if path.startswith(r"\\?\UNC") or path.startswith(r"\\?\\") or path.startswith("\\?\\"):
        return path  # уже длинный путь
    if path.startswith(r"\\"):
        return r"\\?\UNC" + path[1:]
    return r"\\?\\" + os.path.abspath(path)

    
src = r"\\?\UNC\Pczaitenov\159\Ежедневная подача\Галимзянова\14.06.2025 ПС\6-146ГЭС ПС_ca38bd78-7e4f-46a7-aa8c-43b90dfbadfe_Журавлев Алексей Александрович_Галимзянова\ca38bd78-7e4f-46a7-aa8c-43b90dfbadfe_6-146ГЭС ПС_Объяснение_Журавлев Алексей Александрович_Галимзянова_.docx"
dst = r"C:\Temp\test.docx"

src_long = to_long_path(src)

print("[DEBUG] Проверка isfile:", os.path.isfile(src_long))
try:
    shutil.copy2(src_long, dst)
    print("[SUCCESS] Скопирован:", dst)
except Exception as e:
    print("[ERROR]", e)