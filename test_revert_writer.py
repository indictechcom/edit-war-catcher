from src.api.fetcher import fetch_recent_changes
from src.detection.revert_detector import classify_change
from src.db.revert_writer import RevertWriter

# Fetch live data
changes = fetch_recent_changes(limit=50)

# Classify
classified = [classify_change(c) for c in changes]

# Write reverts
writer = RevertWriter()
count = writer.write_reverts(classified)
writer.close()

print(f"Inserted {count} revert events")
