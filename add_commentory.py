import pandas as pd

file_path = (
    r"\\Pczaitenov\159\Ежедневная подача\Галимзянова\Выполненные\Отчетность МВД.xlsx"
)

def add_link(loan_id: str, link: str):
    df = pd.read_excel(file_path)
    new_row = pd.DataFrame({'loan_id': [loan_id], 'link': [link]})
    df = pd.concat([df, new_row], ignore_index=True, axis=0)
    df.to_excel(file_path, index=False)
    print('коммент записан')

