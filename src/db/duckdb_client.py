import duckdb
from src.utils.logger import get_logger

logger = get_logger("duckdb")

class DuckDBClient:
    def __init__(self, db_path):
        self.db_path = db_path
        self.con = duckdb.connect(db_path)

    def execute(self, query, params=None):
        logger.debug(f"Executing query: {query}")
        return self.con.execute(query) if params is None else self.con.execute(query, params)

    def insert_df(self, table_name, df):
        if df.empty:
            return
        self.con.register("df_temp", df)
        self.con.execute(f"INSERT INTO {table_name} SELECT * FROM df_temp")

    def close(self):
        self.con.close()
