from src.db.duckdb_client import DuckDBClient
from src.config import DUCKDB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS revert_events (
  article VARCHAR,
  user VARCHAR,
  revid BIGINT,
  old_revid BIGINT,
  timestamp TIMESTAMP,
  is_vandalism BOOLEAN,
  comment TEXT
);
"""

def init_db():
    db = DuckDBClient(DUCKDB_PATH)
    db.execute(SCHEMA)
    db.close()

if __name__ == "__main__":
    init_db()
