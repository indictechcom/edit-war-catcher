"""
consolidation.py

Responsible for consolidating multiple revert events that should count
as a SINGLE revert according to Wikipedia policy.

Rule implemented:
- Multiple reverts by the SAME user
- On the SAME article
- Within a SHORT time window
→ count as ONE revert for 3RR purposes
"""

from typing import List, Dict
from datetime import timedelta
import duckdb

from src.config import DUCKDB_PATH
from src.utils.logger import get_logger

logger = get_logger("consolidation")

# Wikipedia commonly treats rapid consecutive reverts as one action
CONSOLIDATION_WINDOW_MINUTES = 5


def consolidate_reverts() -> List[Dict]:
    """
    Consolidate revert events stored in DuckDB.

    Returns:
        List[Dict]: Consolidated revert events
    """

    con = duckdb.connect(DUCKDB_PATH)

    query = f"""
    WITH ordered AS (
        SELECT
            article,
            "user",
            timestamp,
            is_vandalism,
            LAG(timestamp) OVER (
                PARTITION BY article, "user"
                ORDER BY timestamp
            ) AS prev_timestamp
        FROM revert_events
        WHERE is_vandalism = FALSE
    ),
    grouped AS (
        SELECT
            *,
            CASE
                WHEN prev_timestamp IS NULL THEN 1
                WHEN timestamp - prev_timestamp > INTERVAL '{CONSOLIDATION_WINDOW_MINUTES} minutes' THEN 1
                ELSE 0
            END AS new_group
        FROM ordered
    ),
    grouped_reverts AS (
        SELECT
            *,
            SUM(new_group) OVER (
                PARTITION BY article, "user"
                ORDER BY timestamp
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
            ) AS group_id
        FROM grouped
    )
    SELECT
        article,
        "user",
        MIN(timestamp) AS first_revert_time,
        COUNT(*) AS raw_revert_count
    FROM grouped_reverts
    GROUP BY article, "user", group_id
    ORDER BY first_revert_time;
    """

    logger.info("Consolidating revert events")
    rows = con.execute(query).fetchall()
    con.close()

    consolidated = [
        {
            "article": r[0],
            "user": r[1],
            "timestamp": r[2],
            "raw_revert_count": r[3],
        }
        for r in rows
    ]

    logger.info("Consolidated %d revert groups", len(consolidated))
    return consolidated
