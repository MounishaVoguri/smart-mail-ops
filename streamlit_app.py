import json
import streamlit as st
from datetime import datetime

from classifier import classify_email
from actions import determine_action
from audit import save_audit


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Smart Mail Ops",
    page_icon="✉️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# PROFESSIONAL CSS
# ============================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #f5f7fb;
}

/* Hide Streamlit branding */
#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    visibility: hidden;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #111827;
    border-right: 1px solid #1f2937;
}

section[data-testid="stSidebar"] * {
    color: #e5e7eb;
}

section[data-testid="stSidebar"] .stButton button {
    background: #1f2937;
    color: white;
    border: 1px solid #374151;
}

/* Main container */
.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1450px;
}

/* Header */
.brand-title {
    font-size: 34px;
    font-weight: 700;
    color: #111827;
    letter-spacing: -1px;
    margin-bottom: 3px;
}

.brand-subtitle {
    color: #6b7280;
    font-size: 15px;
    margin-bottom: 25px;
}

/* Status */
.system-status {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    padding: 6px 12px;
    border-radius: 20px;
    background: #ecfdf5;
    color: #047857;
    font-size: 13px;
    font-weight: 600;
    border: 1px solid #a7f3d0;
}

.status-dot {
    width: 8px;
    height: 8px;
    background: #10b981;
    border-radius: 50%;
}

/* KPI cards */
.kpi-card {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 14px;
    padding: 18px 20px;
    box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
    min-height: 115px;
}

.kpi-label {
    color: #6b7280;
    font-size: 13px;
    font-weight: 500;
    margin-bottom: 7px;
}

.kpi-value {
    color: #111827;
    font-size: 28px;
    font-weight: 700;
}

.kpi-description {
    color: #9ca3af;
    font-size: 12px;
    margin-top: 4px;
}

/* Section headers */
.section-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-top: 30px;
    margin-bottom: 14px;
}

.section-title {
    font-size: 21px;
    font-weight: 650;
    color: #111827;
}

.section-subtitle {
    color: #6b7280;
    font-size: 13px;
    margin-bottom: 16px;
}

/* Panels */
.panel {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 14px;
    padding: 20px;
    box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
}

/* Email card */
.email-card {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 15px;
}

.email-label {
    color: #6b7280;
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: .5px;
}

.email-value {
    color: #111827;
    font-size: 15px;
    font-weight: 500;
    margin-top: 3px;
}

/* Decision cards */
.decision-safe {
    background: #ecfdf5;
    border: 1px solid #a7f3d0;
    border-radius: 12px;
    padding: 16px;
}

.decision-human {
    background: #fffbeb;
    border: 1px solid #fde68a;
    border-radius: 12px;
    padding: 16px;
}

.decision-danger {
    background: #fef2f2;
    border: 1px solid #fecaca;
    border-radius: 12px;
    padding: 16px;
}

.decision-title {
    font-size: 15px;
    font-weight: 650;
    margin-bottom: 4px;
}

.decision-text {
    font-size: 13px;
    color: #4b5563;
}

/* Pills */
.pill {
    display: inline-block;
    padding: 5px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
}

.pill-green {
    background: #dcfce7;
    color: #166534;
}

.pill-yellow {
    background: #fef3c7;
    color: #92400e;
}

.pill-red {
    background: #fee2e2;
    color: #991b1b;
}

.pill-blue {
    background: #dbeafe;
    color: #1d4ed8;
}

/* Footer */
.footer {
    text-align: center;
    color: #9ca3af;
    font-size: 12px;
    margin-top: 35px;
    padding-top: 20px;
    border-top: 1px solid #e5e7eb;
}

/* Buttons */
.stButton > button {
    border-radius: 9px;
    font-weight: 600;
    min-height: 42px;
}

/* Select boxes */
div[data-baseweb="select"] > div {
    border-radius: 9px;
}

/* Text area */
textarea {
    border-radius: 9px !important;
}

/* Progress */
div[data-testid="stProgressBar"] {
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# SESSION STATE
# ============================================================

if "processed_emails" not in st.session_state:
    st.session_state.processed_emails = set()

if "results" not in st.session_state:
    st.session_state.results = []

if "last_result" not in st.session_state:
    st.session_state.last_result = None


# ============================================================
# LOAD DATA
# ============================================================

def load_emails():
    with open(
        "data/emails.json",
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


emails = load_emails()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div style="
            font-size:22px;
            font-weight:700;
            margin-bottom:2px;
        ">
        ✉️ Smart Mail Ops
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div style="
            color:#9ca3af;
            font-size:12px;
            margin-bottom:25px;
        ">
        Autonomous Email Operations
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("### System")

    st.markdown(
        "🟢 Classification Engine"
    )

    st.markdown(
        "🟢 Action Engine"
    )

    st.markdown(
        "🟢 Safety Controls"
    )

    st.markdown(
        "🟢 Duplicate Detection"
    )

    st.markdown(
        "🟢 Audit Logging"
    )

    st.markdown("---")

    st.markdown("### Safety Policy")

    st.markdown(
        """
        <div style="
            background:#1f2937;
            border:1px solid #374151;
            border-radius:10px;
            padding:14px;
            font-size:12px;
            line-height:1.7;
        ">
        <b>Automation Threshold</b><br>
        50% confidence<br><br>

        <b>Low Confidence</b><br>
        Human review required<br><br>

        <b>Duplicate</b><br>
        Automated action blocked
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("")

    if st.button(
        "🔄 Reset Session",
        use_container_width=True
    ):
        st.session_state.processed_emails = set()
        st.session_state.results = []
        st.session_state.last_result = None
        st.rerun()


# ============================================================
# HEADER
# ============================================================

header_left, header_right = st.columns(
    [4, 1]
)

with header_left:

    st.markdown(
        '<div class="brand-title">Email Operations Center</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="brand-subtitle">
        Intelligent classification, controlled automation,
        duplicate prevention and human-in-the-loop review.
        </div>
        """,
        unsafe_allow_html=True
    )

with header_right:

    st.markdown(
        """
        <div style="text-align:right;margin-top:8px;">
            <span class="system-status">
                <span class="status-dot"></span>
                System Operational
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# KPI CALCULATIONS
# ============================================================

total_emails = len(emails)

processed_count = len(
    st.session_state.results
)

automated_count = sum(
    1
    for item in st.session_state.results
    if item["result"].get("automated") is True
)

human_count = sum(
    1
    for item in st.session_state.results
    if item["result"].get("automated") is False
)

duplicate_count = sum(
    1
    for item in st.session_state.results
    if item["result"].get("duplicate") is True
)


# ============================================================
# KPI CARDS
# ============================================================

k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">INBOX</div>
            <div class="kpi-value">{total_emails}</div>
            <div class="kpi-description">Available emails</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with k2:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">PROCESSED</div>
            <div class="kpi-value">{processed_count}</div>
            <div class="kpi-description">Current session</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with k3:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">AUTOMATED</div>
            <div class="kpi-value">{automated_count}</div>
            <div class="kpi-description">Safe actions executed</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with k4:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">HUMAN REVIEW</div>
            <div class="kpi-value">{human_count}</div>
            <div class="kpi-description">Escalated cases</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with k5:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">DUPLICATES</div>
            <div class="kpi-value">{duplicate_count}</div>
            <div class="kpi-description">Blocked duplicates</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# EMAIL WORKSPACE
# ============================================================

st.markdown(
    """
    <div class="section-header">
        <div class="section-title">📨 Email Workspace</div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="section-subtitle">
    Select an email from the simulated inbox and run the autonomous
    decision engine.
    </div>
    """,
    unsafe_allow_html=True
)


email_options = [
    f"{email.get('id')}  •  {email.get('subject')}"
    for email in emails
]

selected_email = st.selectbox(
    "Inbox",
    email_options,
    label_visibility="collapsed"
)

selected_index = email_options.index(
    selected_email
)

email = emails[selected_index]


# ============================================================
# EMAIL DETAILS
# ============================================================

email_left, email_right = st.columns(
    [1.15, 1]
)

with email_left:

    st.markdown(
        """
        <div class="panel">
        <div style="
            font-size:17px;
            font-weight:650;
            margin-bottom:18px;
        ">
        Email Information
        </div>
        """,
        unsafe_allow_html=True
    )

    c1, c2 = st.columns(2)

    with c1:

        st.markdown(
            '<div class="email-label">EMAIL ID</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            f'<div class="email-value">{email.get("id", "-")}</div>',
            unsafe_allow_html=True
        )

    with c2:

        st.markdown(
            '<div class="email-label">SENDER</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            f'<div class="email-value">{email.get("sender", "-")}</div>',
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        '<div class="email-label">SUBJECT</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f'<div class="email-value">{email.get("subject", "-")}</div>',
        unsafe_allow_html=True
    )

    st.markdown("</div>", unsafe_allow_html=True)


with email_right:

    st.markdown(
        """
        <div class="panel">
        <div style="
            font-size:17px;
            font-weight:650;
            margin-bottom:12px;
        ">
        Message Preview
        </div>
        """,
        unsafe_allow_html=True
    )

    st.text_area(
        "Message",
        email.get("body", ""),
        height=145,
        disabled=True,
        label_visibility="collapsed"
    )

    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# PROCESS BUTTON
# ============================================================

st.markdown("")

if st.button(
    "⚡ Analyze Email & Execute Safe Action",
    type="primary",
    use_container_width=True
):

    with st.spinner(
        "Analyzing email and applying safety controls..."
    ):

        classification = classify_email(email)

        result = determine_action(
            email,
            classification,
            processed_emails=st.session_state.processed_emails
        )

        save_audit(
            email,
            classification,
            result["action"],
            result
        )

        st.session_state.results.append(
            {
                "email": email,
                "classification": classification,
                "result": result,
                "timestamp": datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            }
        )

        st.session_state.last_result = {
            "email": email,
            "classification": classification,
            "result": result
        }

    st.success(
        "Email processing completed successfully."
    )


# ============================================================
# DECISION CENTER
# ============================================================

if st.session_state.last_result:

    data = st.session_state.last_result

    classification = data["classification"]

    result = data["result"]

    st.markdown(
        """
        <div class="section-header">
            <div class="section-title">🤖 AI Decision Center</div>
        </div>
        """,
        unsafe_allow_html=True
    )


    d1, d2, d3 = st.columns(3)


    with d1:

        st.markdown(
            """
            <div class="panel">
                <div class="email-label">DETECTED INTENT</div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
                <div style="
                    font-size:20px;
                    font-weight:700;
                    margin-top:8px;
                    color:#1d4ed8;
                ">
                    {classification.get("intent", "UNKNOWN")}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


    with d2:

        confidence = float(
            classification.get(
                "confidence",
                0
            )
        )

        st.markdown(
            """
            <div class="panel">
                <div class="email-label">AI CONFIDENCE</div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
                <div style="
                    font-size:20px;
                    font-weight:700;
                    margin-top:8px;
                ">
                    {confidence * 100:.0f}%
                </div>
            """,
            unsafe_allow_html=True
        )

        st.progress(
            min(max(confidence, 0), 1)
        )

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )


    with d3:

        st.markdown(
            """
            <div class="panel">
                <div class="email-label">FINAL ACTION</div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
                <div style="
                    font-size:18px;
                    font-weight:700;
                    margin-top:8px;
                    color:#111827;
                ">
                    {result.get("action", "UNKNOWN")}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


    # ========================================================
    # SAFETY CONTROL STATUS
    # ========================================================

    st.markdown(
        """
        <div class="section-header">
            <div class="section-title">🛡️ Safety & Governance</div>
        </div>
        """,
        unsafe_allow_html=True
    )


    s1, s2, s3 = st.columns(3)


    with s1:

        if result.get("duplicate"):

            st.markdown(
                """
                <div class="decision-danger">
                    <div class="decision-title">
                    🔴 Duplicate Detected
                    </div>
                    <div class="decision-text">
                    Automated processing was blocked.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        else:

            st.markdown(
                """
                <div class="decision-safe">
                    <div class="decision-title">
                    🟢 Duplicate Check Passed
                    </div>
                    <div class="decision-text">
                    No previously processed copy detected.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )


    with s2:

        if confidence < 0.50:

            st.markdown(
                """
                <div class="decision-danger">
                    <div class="decision-title">
                    🔴 Low Confidence
                    </div>
                    <div class="decision-text">
                    Confidence is below the 50% automation threshold.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        else:

            st.markdown(
                """
                <div class="decision-safe">
                    <div class="decision-title">
                    🟢 Confidence Check Passed
                    </div>
                    <div class="decision-text">
                    Classification meets automation threshold.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )


    with s3:

        if result.get("automated"):

            st.markdown(
                """
                <div class="decision-safe">
                    <div class="decision-title">
                    🟢 Automation Authorized
                    </div>
                    <div class="decision-text">
                    Action can be executed automatically.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        else:

            st.markdown(
                """
                <div class="decision-human">
                    <div class="decision-title">
                    🟡 Human Review Required
                    </div>
                    <div class="decision-text">
                    Automated action has been prevented.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )


    # ========================================================
    # DECISION EXPLANATION
    # ========================================================

    st.markdown(
        """
        <div class="section-header">
            <div class="section-title">📌 Decision Explanation</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="panel">
            <div class="email-label">REASONING</div>
            <div style="
                margin-top:8px;
                color:#374151;
                font-size:14px;
                line-height:1.6;
            ">
                {classification.get(
                    "reason",
                    "No explanation available."
                )}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


    # ========================================================
    # FINAL OUTCOME
    # ========================================================

    st.markdown(
        """
        <div class="section-header">
            <div class="section-title">⚡ Execution Outcome</div>
        </div>
        """,
        unsafe_allow_html=True
    )


    if result.get("automated"):

        st.markdown(
            f"""
            <div class="decision-safe">
                <div class="decision-title">
                🟢 Automated Action Completed
                </div>
                <div class="decision-text">
                {result.get("result", "")}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            f"""
            <div class="decision-human">
                <div class="decision-title">
                🟡 Action Escalated to Human Review
                </div>
                <div class="decision-text">
                {result.get("result", "")}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# PROCESSING HISTORY
# ============================================================

st.markdown(
    """
    <div class="section-header">
        <div class="section-title">📋 Processing History</div>
    </div>
    """,
    unsafe_allow_html=True
)

if not st.session_state.results:

    st.markdown(
        """
        <div class="panel">
            <div style="
                text-align:center;
                color:#9ca3af;
                padding:20px;
            ">
                No emails processed in this session.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

else:

    history = []

    for item in st.session_state.results:

        email_data = item["email"]

        classification_data = item["classification"]

        result_data = item["result"]

        history.append(
            {
                "Email": email_data.get("id"),
                "Subject": email_data.get("subject"),
                "Intent": classification_data.get("intent"),
                "Confidence": (
                    f"{classification_data.get('confidence', 0) * 100:.0f}%"
                ),
                "Action": result_data.get("action"),
                "Mode": (
                    "Automated"
                    if result_data.get("automated")
                    else "Human Review"
                ),
                "Duplicate": (
                    "Yes"
                    if result_data.get("duplicate")
                    else "No"
                ),
                "Time": item["timestamp"]
            }
        )

    st.dataframe(
        history,
        use_container_width=True,
        hide_index=True,
        height=300
    )


# ============================================================
# AUDIT INFORMATION
# ============================================================

st.markdown(
    """
    <div class="section-header">
        <div class="section-title">🔐 Audit & Governance</div>
    </div>
    """,
    unsafe_allow_html=True
)

a1, a2, a3 = st.columns(3)

with a1:

    st.markdown(
        """
        <div class="panel">
            <div class="email-label">AUDIT TRAIL</div>
            <div style="
                font-size:16px;
                font-weight:600;
                margin-top:8px;
            ">
                Enabled
            </div>
            <div style="
                font-size:12px;
                color:#6b7280;
                margin-top:4px;
            ">
                Every processed email is recorded.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with a2:

    st.markdown(
        """
        <div class="panel">
            <div class="email-label">HUMAN-IN-THE-LOOP</div>
            <div style="
                font-size:16px;
                font-weight:600;
                margin-top:8px;
            ">
                Enabled
            </div>
            <div style="
                font-size:12px;
                color:#6b7280;
                margin-top:4px;
            ">
                Uncertain decisions are escalated.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with a3:

    st.markdown(
        """
        <div class="panel">
            <div class="email-label">DUPLICATE PROTECTION</div>
            <div style="
                font-size:16px;
                font-weight:600;
                margin-top:8px;
            ">
                Enabled
            </div>
            <div style="
                font-size:12px;
                color:#6b7280;
                margin-top:4px;
            ">
                Repeated actions are prevented.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        Smart Mail Ops &nbsp;•&nbsp;
        Autonomous Email-to-Action Agent &nbsp;•&nbsp;
        AI Classification &nbsp;•&nbsp;
        Safe Automation &nbsp;•&nbsp;
        Human-in-the-Loop
    </div>
    """,
    unsafe_allow_html=True
)