import pandas as pd
import xlwings as xw
from datetime import date, datetime, timedelta
import datetime as dtime
from docx import Document
import os
import shutil
import zipfile
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
import sys

sys.path.append(r'C:\Users\malyshevea\Documents')
from combine import combine


script_path = r"C:\Users\malyshevea\Documents"

payment_path = r"C:\Users\malyshevea\Desktop\rz_scripts\payments_files"
credit_path = r"C:\Users\malyshevea\Desktop\rz_scripts\cdetails"

# Удаляем папки и пересоздаём их заново
shutil.rmtree(path=payment_path, ignore_errors=True)
shutil.rmtree(path=credit_path, ignore_errors=True)

if not os.path.exists(payment_path):
    os.makedirs(payment_path)

if not os.path.exists(credit_path):
    os.makedirs(credit_path)


def unzip(reestr):
    downloads = r"C:\Users\malyshevea\Downloads"
    payments_extracted = False
    cdetails_extracted = False
    for filename in os.listdir(downloads):
        extract_path = ''
        if f'payments_files - {today_date}' in filename and '.zip' in filename:  
            extract_path = payment_path
            payments_extracted = True  # Обратите внимание на один знак "="
        elif f'cdetails - {today_date}' in filename and '.zip' in filename:
            extract_path = credit_path
            cdetails_extracted = True  # И тут тоже "=" вместо "=="
        if extract_path != '':
            with zipfile.ZipFile(os.path.join(downloads, filename), 'r') as zip_ref:
                zip_ref.extractall(extract_path)
    return payments_extracted, cdetails_extracted


def get_ftp_path(reestr):
    converted_date = today_date.strftime('%d.%m.%Y')
    ftp_path = fr"C:/Users\malyshevea/Desktop/rz_scripts/{reestr}_{converted_date}"
    if os.path.exists(ftp_path):
        return ftp_path
    else:
        print('FTP FOLDER DOES NOT EXIST')
        return None


def get_skorozvon_data(reestr):
    skorozvon_path = os.path.join(script_path, f'{reestr}_call_list_{today_date}.xlsx')
    df = pd.read_excel(skorozvon_path)
    # Фильтруем по нужной группе
    df = df[['Номер кредита', 'Сотрудник']]
    df = df.rename(columns={'Сотрудник': 'eventdate'})
    return df


def get_mvd_data(reestr):
    mvd_path = os.path.join(script_path, f'{reestr}_reestr_mvd_{today_date}.xlsx')
    df = pd.read_excel(mvd_path)
    df = df.drop(['Наименование места работы', 'Адрес места работы', 'eventdate'], axis=1)
    return df


def combine_data(reestr):
    
    users_list = []
    try:
        print('Extracting data from skorozvon')
        skorozvon = get_skorozvon_data(reestr)
        print('Extracting data from mvd')
        mvd = get_mvd_data(reestr)

        combine_data_result = pd.merge(mvd, skorozvon, how='left',
                                       left_on='id', right_on='Номер кредита')

        combine_data_result = combine_data_result.drop(['Unnamed: 0','Номер кредита'], axis=1)
        combine_data_result = combine_data_result.rename(columns={
            'ФИО':'ФИО_клиент',
            'Номер договора займа':'Номер Договора',
            'Дата договора':'Дата Кредита',
            'Сумма кредита':'Сумма Кредита',
            'Дней кредита изначально':'Дней кредита изначально',
            'Регион':'Регион',
            'Валюта кредита':'Валюта кредита',
            'Сумма задолженности по ОД':'Сумма задолженности по ОД',
            'Сумма процентов к погашению':'Сумма процентов к погашению',
            'Сумма штрафов к погашению':'Сумма штрафов к погашению',
            'Общая сумма взыскиваемой зад-ти':'Общая сумма взыскиваемой зад-ти',
            'Дата последнего платежа':'Дата последнего платежа',
            'Сумма последнего платежа':'Сумма последнего платежа',
            'Дата рождения Должника':'Дата рождения Должника',
            'Серия и номер паспорта Должника':'Серия и номер паспорта Должника',
            'Орган выдачи паспорта Должника':'Орган выдачи паспорта Должника',
            'Дата выдачи паспорта Должника':'Дата выдачи паспорта Должника',
            'Телефоны Должника':'Телефоны Должника',
            'Электронный адрес Должника':'Электронный адрес Должника',
            'Адрес регистрации Должника':'Адрес регистрации Должника',
            'Фактический адрес Должника':'Фактический адрес Должника',
            'Премиум-аккаунт сумма':'Премиум-аккаунт сумма',
            'Премиум задолженность':'Премиум задолженность',
            'Юридические услуги сумма':'Юридические услуги сумма',
            'Юридические услуги задолженность':'Юридические услуги задолженность',
            'Дата создания платежа':'Дата создания платежа',
            'Дата приема платежа':'Дата приема платежа',
            'Страхование задолженность':'Страхование задолженность',
            'Телемедицина задолженность':'Телемедицина задолженность',
            'Страхование сумма':'Страхование сумма',
            'Телемедицина сумма':'Телемедицина сумма',
            'Выдача задолженность':'ОД',
            'Номер карты':'Номер карты',
            'inn':'inn',
            'id':'id',
            'eventdate':'сотрудник'
        })
        
        
        return combine_data_result, reestr
    except Exception as e:
        print(e)
        return None


def write_data_to_reestr(data, reestr):
    p_fio = {
        
        'Нечаева Наталья Владимировна':'Нечаевой Натальи Владимировны',
        'Галимзянова Эльвира Сергеевна':'Галимзяновой Эльвиры Сергеевны',
        'Мезитова Эльвина Зеферовна':'Мезитовой Эльвины Зеферовны',
        'Романова Виктория Александровна':'Романовой Виктории Александровны',
        'Мухаметова Жасмин Рузалевна':'Мухаметовой Жасмин Рузалевны',
        'Буторина Любовь Владимировна':'Буториной Любови Владимировны',
        'Куулар Евгения Валентиновна':'Куулар Евгении Валентиновны'
    }

    z_fio = {
        'Нечаева Наталья Владимировна':'ЗАЯВЛЕНИЕ Эквита Нечаева',
        'Галимзянова Эльвира Сергеевна':'ЗАЯВЛЕНИЕ Эквита Галимзянова',
        'Мезитова Эльвина Зеферовна':'ЗАЯВЛЕНИЕ Эквита Мезитова',
        'Романова Виктория Александровна':'ЗАЯВЛЕНИЕ Эквита Романова',
        'Мухаметова Жасмин Рузалевна':'ЗАЯВЛЕНИЕ Эквита Мухаметова',
        'Буторина Любовь Владимировна':'ЗАЯВЛЕНИЕ Эквита Буторина',
        'Куулар Евгения Валентиновна':'ЗАЯВЛЕНИЕ Эквита Куулар',
    }

    base_cols = [
        'Статус','Название файла','Шаблоны для обработки',
        'Дата_выгрузки','ФИО_представитель_им','ФИО_представитель_род'
    ]
    base_df = pd.DataFrame(columns=base_cols)
    df = pd.concat([base_df, data])

    df['Статус'] = 'ok'
    df['Название файла'] = df['id']
    df['Шаблоны для обработки'] = df['сотрудник'].map(z_fio)
    df['Дата_выгрузки'] = today_date
    df['ФИО_представитель_им'] = df['сотрудник']
    df['ФИО_представитель_род'] = df['сотрудник'].map(p_fio)
    
    
    df['сотрудник'] = df['сотрудник'].where(df['Шаблоны для обработки'].notnull(), 'Куулар Евгения Валентиновна')
    df['Статус'] = 'ok'
    df['Название файла'] = df['id']
    df['Шаблоны для обработки'] = df['сотрудник'].map(z_fio)
    df['Дата_выгрузки'] = today_date
    df['ФИО_представитель_им'] = df['сотрудник']
    df['ФИО_представитель_род'] = df['сотрудник'].map(p_fio)
    out_path = os.path.join(script_path,fr'реестр_{reestr}_{today_date}.xlsx')
    
    df.to_excel(out_path, sheet_name='data', index=False)
    print(f"Файл '{out_path}' успешно создан!")


def add_identificator(reestr, save_path):
    reestr_d = {'ps':'ПС', 'dk':'ДК'}
    #in_path = fr'C:\Users\zaitenovri\Desktop\rz_scripts\реестр_{reestr}_{today_date}.xlsx'
    in_path = os.path.join(script_path,fr'реестр_{reestr}_{today_date}.xlsx')
    df = pd.read_excel(in_path, sheet_name='data')
# =============================================================================
#     for column in df.columns:
#         if 'Дата' in column:
#            df[column] = df[column].dt.date
# =============================================================================
    try:
      #  df['Дата_выгрузки'] = pd.to_datetime(df['Дата_выгрузки']).dt.date
        df['Название файла'] = df['Название файла'].astype(str)
        df['Шаблоны для обработки'] = df['Шаблоны для обработки'].astype(str)
        df['ФИО_представитель_им'] = df['ФИО_представитель_им'].astype(str)
        df['ФИО_представитель_род'] = df['ФИО_представитель_род'].astype(str)
    except Exception as e:
        print(e)

    initials = []
    for l in df['ФИО_представитель_им'].str.split():
        try:
            # Берём первые буквы ФИО, например "Миронова Анастасия Андреевна" → "МАА"
            initials.append(l[0][0] + l[1][0] + l[2][0])
        except Exception as e:
            initials.append('XXX')  # на случай, если ФИО неполное

    # Счётчики для каждой тройки инициалов
    if reestr == 'ps':
        row_number = { 
            'ГЭС':1, 'ННВ':1, 'МЭЗ':1, 'РВА':1,'МЖР':1,'БЛВ':1,'КЕВ':1
        }
    else:  # reestr == 'dk'
        row_number = { 
            'ГЭС':1, 'ННВ':1,'МЭЗ':1, 'РВА':1, 'МЖР':1,'БЛВ':1,'КЕВ':1
        }

    identifier = []
    for i in range(len(initials)):
        current_initials = initials[i]
        # Получаем день и месяц из "Дата_выгрузки"
        day = df.loc[i, 'Дата_выгрузки'].day
        month = df.loc[i, 'Дата_выгрузки'].month
        # Собираем идентификатор
        this_id = f"{row_number[current_initials]}-{day}{month}{current_initials} {reestr_d[reestr]}"
        identifier.append(this_id)
        row_number[current_initials] += 1

    df.insert(4, 'Идентификатор', identifier)
    df['идентификатор'] = df['Идентификатор']
    print(df.dtypes)
    out_path = os.path.join(save_path, fr'реестр с идентификатором {reestr_d[reestr]}_{today_date}.xlsx')
  #  out_path = fr'C:\Users\zaitenovri\Desktop\rz_scripts\реестр с идентификатором {reestr_d[reestr]}_{today_date}.xlsx'
    df.to_excel(out_path, index=False, sheet_name='data')
    print(f"Файл с идентификатором '{out_path}' успешно создан!")
    print('Готово')


def format_date_from_excel_number(date_value):
    if pd.isnull(date_value):
        return ''
    try:
        date_obj = pd.to_datetime(date_value, origin='1899-12-30', unit='D')
        return date_obj.strftime('%d.%m.%Y')
    except Exception as e:
        print(f'Error formatting date: {e}')
        return str(date_value)


def main(input_path, output_path):
    """ типы документов править тут """
    doc_types = ['Объяснение', 'ЗАЯВЛЕНИЕ']
    script_path = input_path
    for filename in os.listdir(script_path):
        if 'реестр с идентификатором' in filename and '~$' not in filename and today_date.strftime('%Y-%m-%d') in filename:
            print(filename)
            df = pd.read_excel(os.path.join(script_path, filename), sheet_name='data')
            
            #print(df.columns)
            #return None
          #  print(df.dtypes)
# =============================================================================
#             try:
#                 for column in df.columns:
#                     if 'Дата' in column:
#                       # df[column] = pd.Timestamp(df[column]).dt.days
#                        df[column] = df[column].dt.days
#             except Exception as e:
#                 print(f'Попытка замены колонок дат:\n{e}')
# =============================================================================
# =============================================================================
#             input()
#             print(df.dtypes)
#             input()
# =============================================================================
            #return None
            for index, row in df.iterrows():
# =============================================================================
#                 print(row)
#                 input()
# =============================================================================
                #print(row['Дата договора'])
                #return None
                """Название файла для сохранения"""
                loan_id = row['Название файла']
                client_fio = row['ФИО_клиент']
                surname = row['сотрудник'].split()[0]
                ident = row['идентификатор']

                
                
                for doc_type in doc_types:
                    """ название шаблона править тут """
                    shablon_name = f'{doc_type} Эквита {surname}.docx'
                    #print(shablon_name)
                    if shablon_name in os.listdir(script_path):
                        #print(shablon_name)
                        shablon_doc = Document(os.path.join(script_path, shablon_name))
                        #print(f'шаблон {shablon_name} прочтен')
# =============================================================================
#                         data_replace = {
#                         '[ФИО_представитель_род]': row['ФИО_представитель_род'],
#                         '[Дата Кредита]': format_date_from_excel_number(row['Дата Кредита']),
#                         '[ФИО_клиент]': row['ФИО_клиент'],
#                         '[Регион]': row['Регион'],
#                         '[ОД]': row['ОД'],
#                         '[Дата рождения Должника]': format_date_from_excel_number(row['Дата рождения Должника']),
#                         '[Номер Договора]': row['Номер Договора'],
#                         '[Сумма Кредита]': row['Сумма Кредита'],
#                         '[Страхование сумма]': row['Страхование сумма'],
#                         '[Дата создания платежа]': format_date_from_excel_number(row['Дата создания платежа']),
#                         '[Дата приема платежа]': format_date_from_excel_number(row['Дата приема платежа']),
#                         '[Номер карты]': row['Номер карты'],
#                         '[Серия и номер паспорта Должника]': row['Серия и номер паспорта Должника'],
#                         '[Орган выдачи паспорта Должника]': row['Орган выдачи паспорта Должника'],
#                         '[Дата выдачи паспорта Должника]': format_date_from_excel_number(row['Дата выдачи паспорта Должника']),
#                         '[Адрес регистрации Должника]': row['Адрес регистрации Должника'],
#                         '[Телефоны Должника]': row['Телефоны Должника'],
#                         '[Электронный адрес Должника]': row['Электронный адрес Должника'],
#                         '[Дата_выгрузки]': format_date_from_excel_number(row['Дата_выгрузки']),
#                         '[Общая сумма взыскиваемой зад-ти]': row['Общая сумма взыскиваемой зад-ти'],
#                         '[Сумма задолженности по ОД]': row['Сумма задолженности по ОД'],
#                         '[Страхование задолженность]': row['Страхование задолженность'],
#                         '[Сумма штрафов к погашению]': row['Сумма штрафов к погашению'],
#                         #'[Дата_выгрузки]': row['[Дата_выгрузки'].strftime("%Y%m%d"),
#                         '[ФИО_представитель_им]': row['ФИО_представитель_им'],
#                         '[Общая сумма взыскиваемой зад-ти]': row['Общая сумма взыскиваемой зад-ти'],
#                         '[Сумма процентов к погашению]': row['Сумма процентов к погашению'],
#                         '[Сумма штрафов к погашению]': row['Сумма штрафов к погашению'],
#                         '[Телемедицина сумма]': row['Телемедицина сумма'],
#                         '[Премиум-аккаунт сумма]': row['Премиум-аккаунт сумма'],
#                         '[Юридические услуги сумма]': row['Юридические услуги сумма']
#                                                     }
# =============================================================================
                        
                        
# =============================================================================
#                         print(data_replace)
#                         input()
# =============================================================================
                        
                        data_replace = {
                        '[ФИО_представитель_род]': row['ФИО_представитель_род'],
                        '[Дата Кредита]': row['Дата Кредита'].strftime('%d.%m.%Y'),
                        '[ФИО_клиент]': row['ФИО_клиент'],
                        '[Регион]': row['Регион'],
                        '[ОД]': row['ОД'],
                        '[Дата рождения Должника]': row['Дата рождения Должника'].strftime('%d.%m.%Y'),
                        '[Номер Договора]': row['Номер Договора'],
                        '[Сумма Кредита]': row['Сумма Кредита'],
                        '[Страхование сумма]': row['Страхование сумма'],
                        '[Дата создания платежа]': row['Дата создания платежа'].strftime('%d.%m.%Y'),
                        '[Дата приема платежа]': row['Дата приема платежа'].strftime('%d.%m.%Y'),
                        '[Номер карты]': row['Номер карты'],
                        '[Серия и номер паспорта Должника]': row['Серия и номер паспорта Должника'],
                        '[Орган выдачи паспорта Должника]': row['Орган выдачи паспорта Должника'],
                        '[Дата выдачи паспорта Должника]': row['Дата выдачи паспорта Должника'].strftime('%d.%m.%Y'),
                        '[Адрес регистрации Должника]': row['Адрес регистрации Должника'],
                        '[Телефоны Должника]': row['Телефоны Должника'],
                        '[Электронный адрес Должника]': row['Электронный адрес Должника'],
                        '[Дата_выгрузки]': row['Дата_выгрузки'].strftime('%d.%m.%Y'),
                        '[Общая сумма взыскиваемой зад-ти]': row['Общая сумма взыскиваемой зад-ти'],
                        '[Сумма задолженности по ОД]': row['Сумма задолженности по ОД'],
                        '[Страхование задолженность]': row['Страхование задолженность'],
                        '[Сумма штрафов к погашению]': row['Сумма штрафов к погашению'],
                        #'[Дата_выгрузки]': row['[Дата_выгрузки'].strftime"%Y%m%d",
                        '[ФИО_представитель_им]': row['ФИО_представитель_им'],
                        '[Общая сумма взыскиваемой зад-ти]': row['Общая сумма взыскиваемой зад-ти'],
                        '[Сумма процентов к погашению]': row['Сумма процентов к погашению'],
                        '[Сумма штрафов к погашению]': row['Сумма штрафов к погашению'],
                        '[Телемедицина сумма]': row['Телемедицина сумма'],
                        '[Премиум-аккаунт сумма]': row['Премиум-аккаунт сумма'],
                        '[Юридические услуги сумма]': row['Юридические услуги сумма']
                                                    }
                        
# =============================================================================
#                         print(data_replace)
#                         input()
# =============================================================================
                        try:
                            for paragraph in shablon_doc.paragraphs:
                                #print(paragraph)
                                for key, value in data_replace.items():
                                    if key in paragraph.text:
                                        paragraph.text = paragraph.text.replace(key, str(value))
                            #print('Данные заменены')
                            
                            new_filename = f'{loan_id}_{ident}_{doc_type}_{client_fio}_{surname}_.docx'
                            #print(f'Создаю файл\n{new_filename}')
                            save_path = os.path.join(output_path, new_filename)
                            shablon_doc.save(save_path)
                            #print(f'{new_filename} has been saved in\n{save_path}')
                        except Exception as e:
                            print(f"{e}")
                            continue





def move_data(old_path, new_path):     
    for filename in os.listdir(old_path):
            split = filename.split('_')
            loan_id = split[0]
            client = split[3]
            user = split[4]
            identificator = split[1]
    
            old_filename_abs_path = os.path.join(old_path, filename)

            new_dirname = f'{identificator}_{loan_id}_{client}_{user}'
            new_dir_abs_path = os.path.join(new_path, new_dirname)

            if os.path.exists(os.path.join(new_path, loan_id)) and not os.path.exists(new_dir_abs_path):
                os.rename(os.path.join(new_path, loan_id), new_dir_abs_path)
            else:
                os.makedirs(new_dir_abs_path, exist_ok=True)
    for filename in os.listdir(old_path):
        split = filename.split('_')
        loan_id = split[0]
        client = split[3]
        user = split[4]
        identificator = split[1]
        old_filename_abs_path = os.path.join(old_path, filename)
        print(f'исходный\n{old_filename_abs_path}')
        new_dirname = f'{identificator}_{loan_id}_{client}_{user}'
        new_dir_abs_path = os.path.join(new_path, new_dirname)
        new_filename_abs_path = os.path.join(new_dir_abs_path, filename)
        print(f'конечный\n{new_filename_abs_path}')
        #break
        os.rename(fr'{old_path}\{filename}', fr'{new_path}\{new_dirname}\{filename}')
   
            



def remove_explanation_and_statement(directory_path):
    for dirname in os.listdir(directory_path):
        # Удаляем "_Объяснение" и "_Заявление" из имен папок
        new_dirname = dirname.replace("_Объяснение", "").replace("_Заявление", "")
        
        # Удаляем последние 5 символа из имени папки
        if len(new_dirname) > 6:
            new_dirname = new_dirname[:-6]
        
        old_folder_path = os.path.join(directory_path, dirname)
        new_folder_path = os.path.join(directory_path, new_dirname)
        
        if old_folder_path != new_folder_path:
            os.rename(old_folder_path, new_folder_path)

def rename_folders_in_directory(directory_path, reference_files):
    for filename in reference_files:
        # Разделяем имя файла по символу подчеркивания
        split = filename.split('_')
        if len(split) >= 4:
            loan_id = split[0]
            identificator = split[1]
            # Формируем новое имя папки
            new_folder_name = f'{identificator}_{loan_id}_' + '_'.join(split[2:])
            
            # Ищем существующую папку с loan_id
            for dirname in os.listdir(directory_path):
                if loan_id in dirname:
                    old_folder_path = os.path.join(directory_path, dirname)
                    new_folder_path = os.path.join(directory_path, new_folder_name)
                    
                    # Переименовываем папку
                    os.rename(old_folder_path, new_folder_path)
                    break

def check_data(old_path, new_path):
    reference_files = os.listdir(old_path)
    
    for filename in reference_files:
        # Разделяем имя файла по символу подчеркивания
        split = filename.split('_')
        loan_id = split[0]
        client = split[3]
        user = split[4]
        identificator = split[1]

        # Формируем имя файла
        old_filename_abs_path = os.path.join(old_path, filename)
        
        # Ищем подходящую папку в новой директории по loan_id
        found_folder = None
        for dirname in os.listdir(new_path):
            if loan_id in dirname:
                found_folder = dirname
                break
        
        # Если подходящая папка найдена, используем её
        if found_folder:
            new_folder_path = os.path.join(new_path, found_folder)
        else:
            # Если папка не найдена, создаем новую директорию
            new_dirname = f'{identificator}_{loan_id}_{client}_{user}'
            new_folder_path = os.path.join(new_path, new_dirname)
            os.makedirs(new_folder_path, exist_ok=True)
        
        # Перемещаем файл в найденную или созданную директорию
        os.rename(old_filename_abs_path, os.path.join(new_folder_path, filename))

    # Переименовываем папки в новой директории
    rename_folders_in_directory(new_path, reference_files)
    # Удаляем слова "_Объяснение" и "_Заявление" из имен папок и последние 4 символа
    remove_explanation_and_statement(new_path)


def copy_files(source_dir):
    #source_dir = r'D:\159\ПС. Буфер\БУФЕР ДОСЬЕ'
    target_base_dir = r'\\Pczaitenov\159\Ежедневная подача'

    today = dtime.datetime.now().strftime("%d.%m.%Y")
    
    if not os.path.exists(target_base_dir):
        os.makedirs(target_base_dir, exist_ok=True)

    files = os.listdir(source_dir)
    count_success = 0
    count_failed = 0
    print(f"Обнаружено файлов: {len(files)}")

    for filename in files:
        parts = filename.rsplit('.', 1)[0]
        surname = parts.rsplit('_', 1)[-1]

        target_dir = os.path.join(target_base_dir, surname, today)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir, exist_ok=True)

        source_file = os.path.join(source_dir, filename)
        target_file = os.path.join(target_dir, filename)

        try:
            shutil.move(source_file, target_file)
            count_success += 1
        except Exception as e:
            print(f"Ошибка при перемещении файла {filename}: {e}")
            count_failed += 1
            
    # Итоговое сообщение
    result_message = f"Операция завершена. Успешно перемещено файлов: {count_success}. Ошибок при перемещении: {count_failed}."
    print(result_message)



# C:\Users\zaitenovri\Documents  - сюда реестры
# D:\159\ДК. Буфер\Для объединения - кред, платежки и инфу с сервера (в папке done будет объединение данных отсюда), распаковать сюда содержимое архивов

# D:\159\ПС. Буфер\БУФЕР ДОСЬЕ - досье ПС
# D:\159\ДК. Буфер\БУФЕР ДОСЬЕ - досье ДК


custom_date = date(2025, 5, 30)  # <-- Поменяйте на нужную дату
today_date = custom_date

###############################################################################
#                            Точка запуска (main)
###############################################################################
if __name__ == "__main__":
    # Если нужно распаковать архивы, раскомментируйте (и убедитесь, что они есть)
    # unzip('ps')

    # Собираем данные
    result = combine_data('dk')
    if result is None:
        print("Не удалось собрать данные (None). Проверьте, есть ли нужные файлы!")
    else:
        data, reestr = result
        print('data is not none')
        if reestr == 'ps':
            path = {'output_path':r'\\Pczaitenov\159\ПС. Буфер\БУФЕР ЗАЯВЛЕНИЙ',
                    'input_path':r'\\Pczaitenov\159\ПС. Буфер\МАКРОС',
                    'dossie_path':r'\\Pczaitenov\159\ПС. Буфер\БУФЕР ДОСЬЕ'}
        elif reestr == 'dk':
            path = {'output_path':r'\\Pczaitenov\159\ДК. Буфер\БУФЕР ЗАЯВЛЕНИЙ',
                    'input_path':r'\\Pczaitenov\159\ДК. Буфер\МАКРОС',
                    'dossie_path':r'\\Pczaitenov\159\ДК. Буфер\БУФЕР ДОСЬЕ'}
        # Пишем данные в реестр
        write_data_to_reestr(data, reestr)

        # Добавляем идентификатор
        add_identificator(reestr, path['input_path'])
        
        # Запускаем формирование файлов
        main(path['input_path'], path['output_path'])
        # combine(path['dossie_path'])
        combine()
        
        
        check_data(path['output_path'], path['dossie_path'])
        
        
        copy_files(path['dossie_path'])