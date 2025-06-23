# modules/db_service.py

import logging
import pandas as pd
from typing import Dict, Tuple, Optional

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, Row


class LoanDataService:
    """
    Сервис для получения данных по клиенту из главной БД с помощью dblink.
    """

    def __init__(
        self,
        engine_conn_string: str,
        remote_db_map: Dict[str, str],
        logger: Optional[logging.Logger] = None
    ):
        """
        :param engine_conn_string: DSN для подключения к локальной (OLAP) базе, где настроен dblink.
        :param remote_db_map:   словарь { 'ps': dblink_connstr_for_ps, 'dk': dblink_connstr_for_dk }
        """
        self.logger        = logger or logging.getLogger(__name__)
        self.remote_db_map = remote_db_map
        self.engine: Engine = engine_conn_string

    def _build_query(self, dblink_conn: str, loan_id: str) -> str:
        return f"""
SELECT *
FROM dblink(
    '{dblink_conn}',
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

    def get_code_region(self, loan_type: str, loan_id: str, params=None):
        if loan_type not in self.remote_db_map:
            self.logger.error("Unknown loan_type %r", loan_type)
            return None, None, None, None

        dblink_conn = self.remote_db_map[loan_type]
        query = self._build_query(dblink_conn, loan_id)

        df = pd.read_sql_query(text(query), con=self.engine, params=params)
        if not df.empty:
            fio = df.iloc[0]['fio']
            birthday = df.iloc[0]['birthday']
            region_code = df.iloc[0]['region_code']
            reg_address = df.iloc[0]['reg_address']
            return fio, birthday, region_code, reg_address
        else:
            return None, None, None, None
