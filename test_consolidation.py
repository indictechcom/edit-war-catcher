from src.detection.consolidation import consolidate_reverts

consolidated = consolidate_reverts()

for c in consolidated:
    print(
        c["article"],
        c["user"],
        c["timestamp"],
        "raw:", c["raw_revert_count"]
    )
