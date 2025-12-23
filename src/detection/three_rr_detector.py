"""
three_rr_detector.py

Detects potential violations of Wikipedia's Three-Revert Rule (3RR).

Logic:
- Uses CONSOLIDATED reverts (from consolidation.py)
- Counts reverts by the same user
- On the same article
- Within a rolling 24-hour window
"""

from datetime import timedelta
from typing import List, Dict
import duckdb

from src.config import DUCKDB_PATH
from src.utils.logger import get_logger

logger = get_logger("three_rr_detector")

THREE_RR_LIMIT = 3
WINDOW_HOURS = 24


def detect_three_rr() -> List[Dict]:
    """
    Detect possible Three-Revert Rule violations.

    Returns:
        List[Dict]: List of detected 3RR incidents
    """

    con = duckdb.connect(DUCKDB_PATH)

    query = f"""
    WITH consolidated AS (
        SELECT
            article,
            "user",
            timestamp
        FROM revert_events
        WHERE is_vandalism = FALSE
    ),
    windowed AS (
        SELECT
            article,
            "user",
            timestamp,
            COUNT(*) OVER (
                PARTITION BY article, "user"
                ORDER BY timestamp
                RANGE BETWEEN INTERVAL '{WINDOW_HOURS} hours' PRECEDING AND CURRENT ROW
            ) AS revert_count_24h
        FROM consolidated
    )
    SELECT
        article,
        "user",
        MAX(timestamp) AS last_revert_time,
        MAX(revert_count_24h) AS revert_count
    FROM windowed
    GROUP BY article, "user"
    HAVING MAX(revert_count_24h) >= {THREE_RR_LIMIT}
    ORDER BY last_revert_time DESC;
    """

    logger.info("Detecting possible 3RR violations")
    rows = con.execute(query).fetchall()
    con.close()

    results = [
        {
            "article": r[0],
            "user": r[1],
            "last_revert_time": r[2],
            "revert_count": r[3],
        }
        for r in rows
    ]

    logger.info("Detected %d possible 3RR cases", len(results))
    return results
