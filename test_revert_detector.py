from src.api.fetcher import fetch_recent_changes
from src.detection.revert_detector import classify_change

changes = fetch_recent_changes(limit=20)

for c in changes:
    classified = classify_change(c)
    if classified["is_revert"]:
        print(
            classified["article"],
            classified["user"],
            classified["is_revert"],
            classified["is_vandalism_revert"],
            classified["comment"]
        )
