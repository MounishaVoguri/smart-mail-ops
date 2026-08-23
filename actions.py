CONFIDENCE_THRESHOLD = 0.50


def log_invoice(email):
    return {
        "action": "LOG_INVOICE",
        "result": (
            f"Invoice from {email.get('sender', 'unknown sender')} "
            "successfully logged for processing."
        )
    }


def draft_payment_reply(email):
    return {
        "action": "DRAFT_PAYMENT_REPLY",
        "result": "Payment-status reply drafted for customer review."
    }


def create_follow_up_task(email):
    return {
        "action": "CREATE_FOLLOW_UP_TASK",
        "result": "Dispute follow-up task created for the support team."
    }


def mark_as_spam(email):
    return {
        "action": "MARK_AS_SPAM",
        "result": "Email marked as spam."
    }


def escalate_to_human(email, reason=None):
    if reason is None:
        reason = (
            "The email requires human review "
            "before any automated action."
        )

    return {
        "action": "ESCALATE_TO_HUMAN",
        "result": (
            f"Email escalated to a human reviewer. {reason}"
        )
    }


def generate_email_key(email):
    email_id = email.get("email_id") or email.get("id")

    if email_id:
        return str(email_id)

    sender = str(
        email.get("sender", "")
    ).strip().lower()

    subject = str(
        email.get("subject", "")
    ).strip().lower()

    body = str(
        email.get("body", "")
    ).strip().lower()

    return f"{sender}|{subject}|{body}"


def is_duplicate(email, processed_emails):
    email_key = generate_email_key(email)
    return email_key in processed_emails


def take_action(email, classification, processed_emails=None):

    if processed_emails is None:
        processed_emails = set()

    intent = classification.get(
        "intent",
        "UNKNOWN"
    )

    confidence = float(
        classification.get(
            "confidence",
            0.0
        )
    )

    reason = classification.get(
        "reason",
        "No classification reason available."
    )

    # Duplicate safety control
    if is_duplicate(email, processed_emails):

        result = escalate_to_human(
            email,
            "Possible duplicate detected. "
            "Automated action was blocked."
        )

        return {
            "action": result["action"],
            "result": result["result"],
            "reason": "Duplicate email detected.",
            "confidence": confidence,
            "automated": False,
            "duplicate": True
        }

    # Register email as processed
    processed_emails.add(
        generate_email_key(email)
    )

    # Low confidence safety control
    if confidence < CONFIDENCE_THRESHOLD:

        result = escalate_to_human(
            email,
            "Classification confidence is below "
            f"the {CONFIDENCE_THRESHOLD:.0%} automation threshold."
        )

        return {
            "action": result["action"],
            "result": result["result"],
            "reason": reason,
            "confidence": confidence,
            "automated": False,
            "duplicate": False
        }

    # Unknown intent safety control
    if intent == "UNKNOWN":

        result = escalate_to_human(
            email,
            "The email could not be confidently classified."
        )

        return {
            "action": result["action"],
            "result": result["result"],
            "reason": reason,
            "confidence": confidence,
            "automated": False,
            "duplicate": False
        }

    # Intent to action
    if intent == "INVOICE_SUBMISSION":

        action_result = log_invoice(email)

    elif intent == "PAYMENT_QUERY":

        action_result = draft_payment_reply(email)

    elif intent == "DISPUTE":

        action_result = create_follow_up_task(email)

    elif intent == "SPAM":

        action_result = mark_as_spam(email)

    else:

        action_result = escalate_to_human(
            email,
            f"Unsupported intent: {intent}."
        )

        return {
            "action": action_result["action"],
            "result": action_result["result"],
            "reason": reason,
            "confidence": confidence,
            "automated": False,
            "duplicate": False
        }

    return {
        "action": action_result["action"],
        "result": action_result["result"],
        "reason": reason,
        "confidence": confidence,
        "automated": True,
        "duplicate": False
    }


def execute_action(
    email,
    classification,
    processed_emails=None
):
    return take_action(
        email,
        classification,
        processed_emails
    )


def determine_action(
    email,
    classification,
    confidence=1.0,
    processed_emails=None
):

    if isinstance(classification, str):

        classification = {
            "intent": classification,
            "confidence": confidence,
            "reason": "Manual classification."
        }

    return take_action(
        email,
        classification,
        processed_emails
    )


def process_email_action(
    email,
    intent,
    confidence=1.0
):

    classification = {
        "intent": intent,
        "confidence": confidence,
        "reason": "Manual action-engine test."
    }

    return take_action(
        email,
        classification,
        set()
    )