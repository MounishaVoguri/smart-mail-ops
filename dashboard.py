import streamlit as st
import json
import os
from datetime import datetime


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Smart Mail Ops",
    page_icon="📧",
    layout="wide"
)


# --------------------------------------------------
# LOAD EMAILS
# --------------------------------------------------

def load_emails():

    with open("data/emails.json", "r", encoding="utf-8") as file:
        return json.load(file)


# --------------------------------------------------
# CLASSIFICATION
# --------------------------------------------------

def classify_email(email):

    text = (
        email["subject"] + " " +
        email["body"]
    ).lower()

    if (
        "invoice" in text
        or "billing document" in text
        or "bill attached" in text
    ):
        return {
            "intent": "INVOICE_SUBMISSION",
            "confidence": 0.96,
            "reason": "The email contains invoice or billing information."
        }

    if (
        "payment" in text
        or "paid" in text
        or "transaction" in text
    ):
        return {
            "intent": "PAYMENT_QUERY",
            "confidence": 0.91,
            "reason": "The email discusses a payment or transaction."
        }

    if (
        "dispute" in text
        or "unauthorized charge" in text
        or "charge is incorrect" in text
    ):
        return {
            "intent": "DISPUTE",
            "confidence": 0.94,
            "reason": "The customer is requesting a charge dispute."
        }

    if (
        "free money" in text
        or "winner" in text
        or "click now" in text
        or "lottery" in text
    ):
        return {
            "intent": "SPAM",
            "confidence": 0.99,
            "reason": "The email contains common spam indicators."
        }

    return {
        "intent": "UNKNOWN",
        "confidence": 0.52,
        "reason": "The email does not clearly match a supported intent."
    }


# --------------------------------------------------
# ACTION ENGINE
# --------------------------------------------------

def determine_action(intent, confidence):

    if confidence < 0.60:
        return "ESCALATE_TO_HUMAN"

    actions = {
        "INVOICE_SUBMISSION": "LOG_INVOICE",
        "PAYMENT_QUERY": "DRAFT_PAYMENT_REPLY",
        "DISPUTE": "CREATE_FOLLOW_UP_TASK",
        "SPAM": "MARK_AS_SPAM"
    }

    return actions.get(intent, "ESCALATE_TO_HUMAN")


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

emails = load_emails()

results = []

for email in emails:

    classification = classify_email(email)

    action = determine_action(
        classification["intent"],
        classification["confidence"]
    )

    results.append({
        "email": email,
        "classification": classification,
        "action": action
    })


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.title("📧 Smart Mail Ops")

st.subheader(
    "Autonomous Email-to-Action Agent"
)

st.write(
    "Classify business emails, determine appropriate actions, "
    "and escalate uncertain cases for human review."
)

st.divider()


# --------------------------------------------------
# METRICS
# --------------------------------------------------

total = len(results)

invoice_count = sum(
    r["classification"]["intent"] == "INVOICE_SUBMISSION"
    for r in results
)

payment_count = sum(
    r["classification"]["intent"] == "PAYMENT_QUERY"
    for r in results
)

dispute_count = sum(
    r["classification"]["intent"] == "DISPUTE"
    for r in results
)

spam_count = sum(
    r["classification"]["intent"] == "SPAM"
    for r in results
)

human_count = sum(
    r["action"] == "ESCALATE_TO_HUMAN"
    for r in results
)


col1, col2, col3, col4, col5, col6 = st.columns(6)

col1.metric("Total Emails", total)
col2.metric("Invoices", invoice_count)
col3.metric("Payments", payment_count)
col4.metric("Disputes", dispute_count)
col5.metric("Spam", spam_count)
col6.metric("Human Review", human_count)


st.divider()


# --------------------------------------------------
# EMAIL TABLE
# --------------------------------------------------

st.header("📋 Email Processing")

for r in results:

    email = r["email"]
    classification = r["classification"]
    action = r["action"]

    confidence = classification["confidence"]

    if action == "ESCALATE_TO_HUMAN":
        status = "⚠️ Human Review"
    else:
        status = "✅ Automated"


    with st.expander(
        f"{email['id']} — {email['subject']}"
    ):

        col1, col2 = st.columns(2)

        with col1:

            st.write("### Email")

            st.write(
                f"**From:** {email['sender']}"
            )

            st.write(
                f"**Subject:** {email['subject']}"
            )

            st.write(
                f"**Body:** {email['body']}"
            )

        with col2:

            st.write("### AI Analysis")

            st.write(
                f"**Intent:** "
                f"`{classification['intent']}`"
            )

            st.write(
                f"**Confidence:** "
                f"{confidence * 100:.0f}%"
            )

            st.progress(confidence)

            st.write(
                f"**Reason:** "
                f"{classification['reason']}"
            )

            st.write(
                f"**Action:** `{action}`"
            )

            st.write(
                f"**Status:** {status}"
            )


# --------------------------------------------------
# AUDIT TRAIL
# --------------------------------------------------

st.divider()

st.header("🔍 Audit Trail")

audit_file = "audit_log.json"

if os.path.exists(audit_file):

    with open(
        audit_file,
        "r",
        encoding="utf-8"
    ) as file:

        audit_records = [
            json.loads(line)
            for line in file
            if line.strip()
        ]

    if audit_records:

        for record in reversed(audit_records[-10:]):

            st.write(
                f"**{record['timestamp']}** | "
                f"{record['email_id']} | "
                f"{record['intent']} | "
                f"{record['action']}"
            )

    else:

        st.info("No audit records available.")

else:

    st.info("No audit log found.")


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "Smart Mail Ops | AI-assisted email classification "
    "with controlled automation and human oversight"
)