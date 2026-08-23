import re


# ---------------------------------------------------------
# Offline SmartMailOps Email Classifier
# ---------------------------------------------------------

INTENT_KEYWORDS = {

    "INVOICE_SUBMISSION": {
        "invoice": 5,
        "invoicing": 4,
        "bill": 4,
        "billing": 4,
        "statement": 3,
        "amount due": 4,
        "invoice number": 5,
        "invoice submission": 6,
        "submit invoice": 6,
        "attached invoice": 6,
    },

    "PAYMENT_QUERY": {
        "payment": 4,
        "paid": 3,
        "transaction": 4,
        "payment status": 6,
        "payment not received": 7,
        "not received": 4,
        "transfer": 3,
        "refund": 3,
        "payment issue": 5,
        "payment problem": 5,
    },

    "DISPUTE": {
        "dispute": 7,
        "disputed": 7,
        "unauthorized": 6,
        "fraud": 6,
        "fraudulent": 6,
        "chargeback": 7,
        "incorrect charge": 6,
        "wrong charge": 6,
        "challenge charge": 6,
        "dispute charge": 8,
    },

    "SPAM": {
        "winner": 7,
        "won": 5,
        "lottery": 7,
        "prize": 6,
        "free money": 8,
        "claim now": 7,
        "click now": 6,
        "congratulations": 5,
        "you won": 7,
        "urgent offer": 5,
        "limited time offer": 5,
    }
}


def normalize_text(text):
    """
    Convert email text into a normalized form.
    """
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def calculate_scores(text):
    """
    Calculate weighted scores for every supported intent.
    """

    scores = {
        "INVOICE_SUBMISSION": 0,
        "PAYMENT_QUERY": 0,
        "DISPUTE": 0,
        "SPAM": 0,
    }

    matched_keywords = {
        "INVOICE_SUBMISSION": [],
        "PAYMENT_QUERY": [],
        "DISPUTE": [],
        "SPAM": [],
    }

    for intent, keywords in INTENT_KEYWORDS.items():

        for keyword, weight in keywords.items():

            if keyword in text:
                scores[intent] += weight
                matched_keywords[intent].append(keyword)

    return scores, matched_keywords


def calculate_confidence(scores, selected_intent):

    highest_score = scores[selected_intent]

    if highest_score == 0:
        return 0.0

    total_score = sum(scores.values())

    if total_score == 0:
        return 0.0

    # Basic score-based confidence
    confidence = highest_score / total_score

    # Give a small boost when the classification has
    # strong evidence.
    if highest_score >= 7:
        confidence += 0.10
    elif highest_score >= 5:
        confidence += 0.05

    # Keep confidence between 0 and 0.99
    confidence = min(confidence, 0.99)

    return round(confidence, 2)


def classify_email(email):

    subject = email.get("subject", "")
    body = email.get("body", "")
    sender = email.get("sender", "")

    # Combine relevant email information
    combined_text = normalize_text(
        subject + " " + body
    )

    scores, matched_keywords = calculate_scores(combined_text)

    # -----------------------------------------------------
    # No supported intent found
    # -----------------------------------------------------

    if max(scores.values()) == 0:

        return {
            "intent": "UNKNOWN",
            "confidence": 0.35,
            "reason": (
                "The email does not contain enough information "
                "to match a supported business intent."
            )
        }

    # -----------------------------------------------------
    # Find highest scoring intent
    # -----------------------------------------------------

    selected_intent = max(
        scores,
        key=scores.get
    )

    highest_score = scores[selected_intent]

    confidence = calculate_confidence(
        scores,
        selected_intent
    )

    matched = matched_keywords[selected_intent]

    # -----------------------------------------------------
    # Ambiguous classification
    # -----------------------------------------------------

    sorted_scores = sorted(
        scores.values(),
        reverse=True
    )

    if (
        len(sorted_scores) >= 2
        and sorted_scores[0] == sorted_scores[1]
    ):

        return {
            "intent": "UNKNOWN",
            "confidence": 0.45,
            "reason": (
                "The email contains indicators for multiple "
                "supported intents and requires human review."
            )
        }

    # -----------------------------------------------------
    # Low confidence
    # -----------------------------------------------------

    if confidence < 0.50:

        return {
            "intent": "UNKNOWN",
            "confidence": confidence,
            "reason": (
                "The available email information is not "
                "strong enough for an automated decision."
            )
        }

    # -----------------------------------------------------
    # Generate explanation
    # -----------------------------------------------------

    reason = (
        f"The email was classified as {selected_intent} "
        f"based on the detected indicators: "
        f"{', '.join(matched[:5])}."
    )

    return {
        "intent": selected_intent,
        "confidence": confidence,
        "reason": reason
    }