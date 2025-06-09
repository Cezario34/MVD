import pandas as pd

file_path = (
    r"\\servmfo\Отдел взыскания и верификации\ВЗЫСКАНИЕ КЭШ-Ю\ОТЧЕТЫ РУКОВОДИТЕЛЕЙ"
    r"\0 Отчетность отдел\1 Списочный реестр задач\!Шаблон\Отчетности\Операционные отчеты"
    r"\Рейтинги сотрудников\Отчетность мвд\Отчетность МВД.xlsx"
)

def add_link(loan_id: str, link: str):
    df = pd.read_excel(file_path)
    new_row = pd.DataFrame({'loan_id': [loan_id], 'link': [link]})
    df = pd.concat([df, new_row], ignore_index=True, axis=0)
    df.to_excel(file_path, index=False)
    print('коммент записан')

