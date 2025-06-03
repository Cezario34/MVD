from config_data import conn_string, main_db_config
from sqlalchemy import create_engine, text
import pandas as pd

def get_query(bd, loan_id):
    return f"""
SELECT *
FROM dblink(
    '{bd}',
	$$
	SELECT

    substring(addresses->'reg_address'->>'region_kladr_id' FROM 1 FOR 2) AS region_code
    from loans join clients on loans.profile_id = clients.profile_id
    
     where loans.id = '{loan_id}'
	$$
) as t1 (region_code int)
"""


def get_code(bd, loan_id, params=None):
    engine_olap = create_engine(conn_string)
    query=get_query(bd, loan_id)
    df = pd.read_sql_query(text(query), con=engine_olap, params=params)
    if not df.empty:
        return df.iloc[0, 0]  # возвращает просто значение без индекса и колонки
    else:
        return None  


print(get_code(main_db_config.ps,'10656835-1a26-4357-bfe8-3fe25421e97c'))