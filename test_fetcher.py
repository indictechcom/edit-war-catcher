from src.api.fetcher import fetch_recent_changes

changes = fetch_recent_changes(limit=10)

for c in changes:
    print(
        c.get("title"),
        c.get("user"),
        c.get("comment"),
        c.get("tags")
    )
