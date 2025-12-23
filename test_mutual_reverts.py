from src.detection.mutual_revert_detector import detect_mutual_reverts

cases = detect_mutual_reverts()

for c in cases:
    print(
        c["article"],
        c["user_a"],
        c["user_b"],
        "A:", c["reverts_user_a"],
        "B:", c["reverts_user_b"],
        "last:", c["last_interaction"]
    )
