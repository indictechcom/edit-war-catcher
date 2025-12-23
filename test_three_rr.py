from src.detection.three_rr_detector import detect_three_rr

cases = detect_three_rr()

for c in cases:
    print(
        c["article"],
        c["user"],
        "reverts:", c["revert_count"],
        "last:", c["last_revert_time"]
    )
