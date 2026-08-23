import json
from datetime import datetime


def save_audit(email, classification, action, result):

    record = {
        "timestamp": datetime.now().isoformat(
            timespec="seconds"
        ),
        "email_id": email["id"],
        "sender": email["sender"],
        "subject": email["subject"],
        "intent": classification["intent"],
        "confidence": classification["confidence"],
        "reason": classification["reason"],
        "action": action,
        "result": result
    }

    with open("audit_log.json", "a", encoding="utf-8") as file:
        file.write(json.dumps(record) + "\n")