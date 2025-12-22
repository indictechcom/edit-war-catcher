"""
revert_detector.py

Responsible for classifying edits as:
- revert
- vandalism revert
- normal edit

This module does NOT touch the database.
It only analyzes a single recentchanges item and returns structured results.
"""

from typing import Dict, Any
from src.utils.logger import get_logger

logger = get_logger("revert_detector")

# Strong revert indicators from tags (high confidence)
REVERT_TAG_KEYWORDS = (
    "mw-rollback",
    "mw-undo",
    "mw-reverted",
    "rollback",
    "revert"
)

# Common revert keywords in edit summaries (medium confidence)
REVERT_SUMMARY_KEYWORDS = (
    "revert",
    "reverted",
    "undo",
    "undid",
    "rv",
    "restore",
    "restored"
)

# Keywords strongly suggesting vandalism reverts (policy exemptions for 3RR)
VANDALISM_KEYWORDS = (
    "vandal",
    "vandalism",
    "rvv",
    "reverted vandalism",
    "undo vandalism",
    "test edit",
    "spam"
)


def _contains_keyword(text: str, keywords: tuple[str, ...]) -> bool:
    """Case-insensitive keyword check."""
    if not text:
        return False
    text = text.lower()
    return any(k in text for k in keywords)


def is_revert(change: Dict[str, Any]) -> bool:
    """
    Determine whether an edit is a revert.

    Priority:
    1. Tags (strong signal)
    2. Summary keywords (weaker but common)
    """

    tags = change.get("tags", []) or []
    comment = change.get("comment", "") or ""

    # 1️⃣ Tag-based detection (highest confidence)
    for tag in tags:
        tag_lower = tag.lower()
        if _contains_keyword(tag_lower, REVERT_TAG_KEYWORDS):
            logger.debug("Revert detected via tag: %s", tag)
            return True

    # 2️⃣ Summary-based detection
    if _contains_keyword(comment, REVERT_SUMMARY_KEYWORDS):
        logger.debug("Revert detected via summary: %s", comment)
        return True

    return False


def is_vandalism_revert(change: Dict[str, Any]) -> bool:
    """
    Determine whether a revert is likely vandalism-related.

    These reverts are generally exempt from 3RR enforcement.
    """

    comment = change.get("comment", "") or ""
    tags = change.get("tags", []) or []

    # Summary-based vandalism detection
    if _contains_keyword(comment, VANDALISM_KEYWORDS):
        logger.debug("Vandalism revert detected via summary: %s", comment)
        return True

    # Rollback tool + vandalism wording is strong signal
    for tag in tags:
        if "rollback" in tag.lower() and "vandal" in comment.lower():
            logger.debug("Vandalism revert detected via rollback tag")
            return True

    return False


def classify_change(change: Dict[str, Any]) -> Dict[str, Any]:
    """
    Classify a single recent change.

    Returns a normalized dict that downstream logic can store or analyze.
    """

    revert = is_revert(change)
    vandalism = revert and is_vandalism_revert(change)

    result = {
        "article": change.get("title"),
        "user": change.get("user"),
        "revid": change.get("revid"),
        "old_revid": change.get("old_revid"),
        "timestamp": change.get("timestamp"),
        "comment": change.get("comment"),
        "tags": change.get("tags", []),
        "is_revert": revert,
        "is_vandalism_revert": vandalism
    }

    logger.debug(
        "Classified change | article=%s user=%s revert=%s vandalism=%s",
        result["article"],
        result["user"],
        revert,
        vandalism
    )

    return result
