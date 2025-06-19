import pandas as pd

from config_data import conn_string, main_db_config
from sqlalchemy import create_engine, text


def get_query(bd, loan_id):
    return f"""
SELECT *
FROM dblink(
    '{bd}',
    $$
    SELECT
        concat(surname, ' ', name, ' ', midname) as fio,
        TO_CHAR(birthdate, 'DD-MM-YYYY') as birthday,
        substring(addresses->'reg_address'->>'region_kladr_id' FROM 1 FOR 2) AS region_code,
        addresses_label->'reg_address' as reg_address
    FROM loans
    JOIN clients ON loans.profile_id = clients.profile_id
    WHERE loans.id = '{loan_id}'
      AND coalesce(amount_principal_accrued,0) - coalesce(amount_principal_paid, 0) >= 500
      AND NOT EXISTS (
        SELECT 1 FROM tags x
        WHERE (x.loan_id = loans.id OR x.client_id = clients.id)
          AND x.tag_type_id IN ('33','31','28','27','26')
      )
    $$
) AS t1 (
    fio varchar,
    birthday varchar,
    region_code varchar,
    reg_address varchar
)
WHERE
    NOT (
        reg_address ILIKE '%Аминьевский мост%' OR
        reg_address ILIKE '%Аминьевское шоссе%' OR
        reg_address ILIKE '%Большая Очаковская улица%' OR
        reg_address ILIKE '%Веерная улица%' OR
        reg_address ILIKE '%Верейская улица%' OR
        reg_address ILIKE '%Генерала Дорохова%' OR
        reg_address ILIKE '%Елены Колесовой%' OR
        reg_address ILIKE '%Лобачевского%' OR
        reg_address ILIKE '%Марии Поливановой%' OR
        reg_address ILIKE '%Матвеевская улица%' OR
        reg_address ILIKE '%Мичуринский проспект%' OR
        reg_address ILIKE '%Наташи Ковшовой%' OR
        reg_address ILIKE '%Нежинская улица%' OR
        reg_address ILIKE '%Озёрная площадь%' OR
        reg_address ILIKE '%Озёрная улица%' OR
        reg_address ILIKE '%Очаковский%' OR
        reg_address ILIKE '%Очаковское шоссе%' OR
        reg_address ILIKE '%Пржевальского%' OR
        reg_address ILIKE '%Проектируемый проезд N 1438%' OR
        reg_address ILIKE '%Проектируемый проезд N 1980%' OR
        reg_address ILIKE '%Проектируемый проезд N 5231%' OR
        reg_address ILIKE '%Рябиновая улица%' OR
        reg_address ILIKE '%Староволынская улица%' OR
        reg_address ILIKE '%Стройкомбината%' OR
        reg_address ILIKE '%Троекуровский проезд%' OR
        reg_address ILIKE '%Брянск%' OR
        reg_address ILIKE '%Курск%' OR
        reg_address ILIKE '%Белгород%' OR
        reg_address ILIKE '%Белгородcкая%' OR
        reg_address ILIKE '%Брянская%' OR
        reg_address ILIKE '%Курская обл%'
    )
LIMIT 1;

"""


def get_code_region(bd: str, loan_id: str, params=None):
    """
    На вход получает строку подключения к мейн бд и номер договора.
    Возвращает fio, birthday, region_code (или None, если не найдено).
    """
    engine_olap = create_engine(conn_string)
    query = get_query(bd, loan_id)
    df = pd.read_sql_query(text(query), con=engine_olap, params=params)
    if not df.empty:
        fio = df.iloc[0]['fio']
        birthday = df.iloc[0]['birthday']
        region_code = df.iloc[0]['region_code']
        reg_address = df.iloc[0]['reg_address']
        return fio, birthday, region_code, reg_address
    else:
        return None, None, None, None


bd = {
    'ps' : main_db_config.ps,
    'dk': main_db_config.dk 
}


