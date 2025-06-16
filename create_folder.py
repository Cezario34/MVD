import os
from datetime import date


current_date = date.today()
format_date = current_date.strftime("%d.%m.%Y")


bd = ['ПС', 'ДК']
for i in bd:
    starter_root = fr"\\Pczaitenov\159\Ежедневная подача\Галимзянова\Выполненные\{format_date}\{i}"
    if not os.path.exists(starter_root):
        os.makedirs(starter_root)
    else:
        print(f"Папка `{starter_root}` уже существует!")