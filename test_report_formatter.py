from src.reporter.report_formatter import format_full_report

# Fake sample data
three_rr = [
    {
        "article": "Test Article",
        "user": "ExampleUser",
        "revert_count": 3,
        "last_revert_time": __import__("datetime").datetime.utcnow()
    }
]

mutual = [
    {
        "article": "Edit War Page",
        "user_a": "UserA",
        "user_b": "UserB",
        "reverts_user_a": 2,
        "reverts_user_b": 2,
        "last_interaction": __import__("datetime").datetime.utcnow()
    }
]

print(format_full_report(three_rr, mutual))
