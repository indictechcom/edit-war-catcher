"""
mutual_revert_detector.py

Detects mutual revert patterns (edit wars) between two users on the same article.

Definition used:
- Two distinct users
- Reverting on the SAME article
- Within a rolling time window
- Each user has reverted at least MIN_REVERTS times
"""

from typing import List, Dict
import duckdb

from src.config import DUCKDB_PATH
from src.utils.logger import get_logger

logger = get_logger("mutual_revert_detector")

WINDOW_HOURS = 24
MIN_REVERTS_EACH = 2  # conservative default


def detect_mutual_reverts() -> List[Dict]:
    """
    Detect mutual revert edit wars.

    Returns:
        List[Dict]: Detected mutual revert incidents
    """

    con = duckdb.connect(DUCKDB_PATH)

    query = f"""
    WITH base AS (
        SELECT
            article,
            "user",
            timestamp
        FROM revert_events
        WHERE is_vandalism = FALSE
    ),
    pairs AS (
        SELECT
            a.article AS article,
            a."user" AS user_a,
            b."user" AS user_b,
            a.timestamp AS ts_a,
            b.timestamp AS ts_b
        FROM base a
        JOIN base b
          ON a.article = b.article
         AND a."user" < b."user"
         AND ABS(EPOCH(a.timestamp) - EPOCH(b.timestamp)) <= {WINDOW_HOURS} * 3600
    ),
    counts AS (
        SELECT
            article,
            user_a,
            user_b,
            COUNT(*) FILTER (WHERE ts_a IS NOT NULL) AS reverts_a,
            COUNT(*) FILTER (WHERE ts_b IS NOT NULL) AS reverts_b,
            MAX(GREATEST(ts_a, ts_b)) AS last_interaction
        FROM pairs
        GROUP BY article, user_a, user_b
    )
    SELECT
        article,
        user_a,
        user_b,
        reverts_a,
        reverts_b,
        last_interaction
    FROM counts
    WHERE reverts_a >= {MIN_REVERTS_EACH}
      AND reverts_b >= {MIN_REVERTS_EACH}
    ORDER BY last_interaction DESC;
    """

    logger.info("Detecting mutual revert edit wars")
    rows = con.execute(query).fetchall()
    con.close()

    results = [
        {
            "article": r[0],
            "user_a": r[1],
            "user_b": r[2],
            "reverts_user_a": r[3],
            "reverts_user_b": r[4],
            "last_interaction": r[5],
        }
        for r in rows
    ]

    logger.info("Detected %d mutual revert cases", len(results))
    return results
