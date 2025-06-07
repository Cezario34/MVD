from config_data import conn_string, main_db_config
from sqlalchemy import create_engine, text
import pandas as pd
from loans_cheker import get_loan_id

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
    $$
) AS t1 (
    fio varchar,
    birthday varchar,
    region_code varchar,
    reg_address varchar
);
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
        return fio, birthday, region_code,reg_address
    else:
        return None, None, None

bd = {
    'ps' : main_db_config.ps,
    'dk': main_db_config.dk 
}