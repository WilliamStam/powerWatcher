import logging
import sqlite3
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class TableReturn:
    def __init__(self, table=None, columns=None, unique=None):
        self.table = table
        self.columns = columns
        self.unique = unique

    def __repr__(self):
        return self.table

    def keys(self):
        return self.columns

    def insertSql(self, values: dict = dict(), upsert: dict=dict()):
        sql_columns = ", \n    ".join([x for x in self.keys()])
        sql_values = ", \n    ".join([f":{x}" for x in self.keys()])
        sql = (f"INSERT INTO {self.table} (\n    {sql_columns}\n) VALUES (\n    {sql_values}\n)")
        if upsert:
            upsertsql = list()
            for k,v in upsert.items():
                upsertsql.append(f"{k}={v}")
            if len(upsertsql):
                upsertsql = ", ".join(upsertsql)
                unq_cols = ",".join(self.unique)
                sql = f"{sql} ON CONFLICT({unq_cols}) DO UPDATE SET {upsertsql};"

        vvv = dict()
        for k in self.keys():
            vvv[k] = values.get(k, None)
        return (sql, vvv)


class Database():
    def __init__(self, filename: str = None):
        self.filename = filename
        logger.debug(f"Init database: {self.filename}")

    def createTable(
        self, tablename: str = None,
        columns: dict = dict(),
        indexes: dict = dict(),
        unique: list = list(),
    ) -> TableReturn:
        c = list()
        for k, v in columns.items():
            c.append(f"    {k} {v}")

        c = ", \n".join(c)

        logger.debug(f"Checking table: {tablename}")
        sql = f"CREATE TABLE IF NOT EXISTS {tablename} (\n{c}\n)"

        with self.exec() as cursor:
            cursor.execute(sql)

        with self.exec() as cursor:
            for k, v in indexes.items():
                if len(v):
                    ind_columns = ",".join([f"{f}" for f in v])
                    s = f"CREATE INDEX IF NOT EXISTS {k} ON {tablename}({ind_columns});"
                    cursor.execute(s)

            if len(unique):
                ind_columns = ",".join([f"{f}" for f in unique])
                s = f"CREATE UNIQUE INDEX IF NOT EXISTS unique_indx ON {tablename}({ind_columns});"
                cursor.execute(s)

        return TableReturn(table=tablename, columns=columns, unique=unique)

    @contextmanager
    def exec(self):
        try:
            connection = sqlite3.connect(self.filename)
            cursor = connection.cursor()
            logger.debug(f"Opening connection: {self.filename}")
            try:
                yield cursor
            finally:
                if connection.total_changes:
                    connection.commit()
                cursor.close()
                connection.close()
                logger.debug(f"Closing connection: {self.filename}")
        except Exception as e:
            logger.error(f"Error: {str(e)}")
