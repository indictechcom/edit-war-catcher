"""
revert_writer.py

Responsible for writing detected revert events into DuckDB.

This module:
- Accepts classified changes from revert_detector
- Filters only revert edits
- Writes them to DuckDB in a safe, batched manner

No detection logic here.
No API calls here.
"""

from typing import List, Dict, Any
import pandas as pd

from src.db.duckdb_client import DuckDBClient
from src.config import DUCKDB_PATH
from src.utils.logger import get_logger

logger = get_logger("revert_writer")


class RevertWriter:
    def __init__(self):
        self.db = DuckDBClient(DUCKDB_PATH)

    def write_reverts(self, classified_changes: List[Dict[str, Any]]) -> int:
        """
        Persist revert events into DuckDB.

        Args:
            classified_changes (List[Dict]): Output from classify_change()

        Returns:
            int: Number of revert rows written
        """

        # Keep only reverts
        revert_rows = [
            {
                "article": c["article"],
                "user": c["user"],
                "revid": c["revid"],
                "old_revid": c["old_revid"],
                "timestamp": c["timestamp"],
                "is_vandalism": c["is_vandalism_revert"],
                "comment": c["comment"],
            }
            for c in classified_changes
            if c.get("is_revert")
        ]

        if not revert_rows:
            logger.info("No reverts to write")
            return 0

        df = pd.DataFrame(revert_rows)

        try:
            self.db.insert_df("revert_events", df)
            logger.info("Inserted %d revert events into DuckDB", len(df))
            return len(df)

        except Exception as e:
            logger.error("Failed to write revert events: %s", e)
            raise

    def close(self):
        self.db.close()
