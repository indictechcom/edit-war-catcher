"""
main.py

Entry point for EditWarCatcherBot.

Pipeline:
1. Fetch recent Wikipedia changes
2. Detect reverts
3. Persist revert events to DuckDB
4. Consolidate revert actions
5. Detect 3RR violations
6. Detect mutual revert edit wars
7. Generate WikiText report
"""

from src.api.fetcher import fetch_recent_changes
from src.detection.revert_detector import classify_change
from src.db.revert_writer import RevertWriter
from src.detection.consolidation import consolidate_reverts
from src.detection.three_rr_detector import detect_three_rr
from src.detection.mutual_revert_detector import detect_mutual_reverts
from src.reporter.report_formatter import format_full_report
from src.utils.logger import get_logger

logger = get_logger("main")


def run():
    logger.info("Starting EditWarCatcherBot run")

    # 1️⃣ Fetch recent changes
    changes = fetch_recent_changes(limit=200)

    if not changes:
        logger.warning("No recent changes fetched, exiting")
        return

    # 2️⃣ Classify changes
    classified = [classify_change(c) for c in changes]

    # 3️⃣ Persist reverts
    writer = RevertWriter()
    revert_count = writer.write_reverts(classified)
    writer.close()

    logger.info("Persisted %d revert events", revert_count)

    # 4️⃣ Consolidation (policy correctness)
    consolidated = consolidate_reverts()
    logger.info("Consolidated into %d revert actions", len(consolidated))

    # 5️⃣ Detect 3RR violations
    three_rr_cases = detect_three_rr()

    # 6️⃣ Detect mutual revert edit wars
    mutual_cases = detect_mutual_reverts()

    # 7️⃣ Format report
    report = format_full_report(three_rr_cases, mutual_cases)

    # For now, just print the report
    # (later: post using Pywikibot or save to file)
    print("\n" + "=" * 80 + "\n")
    print(report)
    print("\n" + "=" * 80 + "\n")

    logger.info("EditWarCatcherBot run completed")


if __name__ == "__main__":
    run()
