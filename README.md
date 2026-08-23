# SmartMailOps

## Autonomous Email-to-Action Agent

SmartMailOps is an intelligent email automation system that classifies business emails, assigns confidence scores, performs controlled actions, and escalates uncertain cases to human reviewers.

## Problem Statement

Organizations receive large volumes of business emails related to invoices, payments, disputes, and other requests. Manually processing these emails is time-consuming and can result in inconsistent responses and missed actions.

SmartMailOps addresses this problem by automatically analyzing incoming emails, identifying their intent, and routing them to appropriate business actions while keeping humans in the loop for uncertain decisions.

## Key Features

- Offline email intent classification
- Confidence-based decision making
- Invoice email processing
- Payment query handling
- Dispute detection
- Spam detection
- Human approval and rejection workflow
- Automatic action routing
- Audit logging
- Streamlit dashboard
- Sample email dataset

## Supported Intents

1. INVOICE_SUBMISSION
2. PAYMENT_QUERY
3. DISPUTE
4. SPAM
5. UNKNOWN

## System Workflow

Email
→ Classification
→ Confidence Scoring
→ Action Routing
→ Human Review when required
→ Audit Logging
→ Dashboard

## Technology Stack

- Python
- Streamlit
- Pandas
- NumPy
- Python-dotenv

## Project Structure

smart-mail-ops/

├── app.py

├── classifier.py

├── actions.py

├── audit.py

├── dashboard.py

├── streamlit_app.py

├── data/

│   └── emails.json

├── requirements.txt

├── .gitignore

└── README.md

## Running the Project

Create a virtual environment and install the dependencies listed in requirements.txt.

Then run:

python -m streamlit run streamlit_app.py

Open the local Streamlit URL shown in the terminal.

## Human-in-the-Loop

Emails with uncertain classification are not automatically processed. They are sent to human review, where the reviewer can approve or reject the proposed action.

## Safety

The system uses confidence-based routing to reduce the risk of incorrect automated actions.

## Future Improvements

- Integration with real email services
- Advanced NLP/LLM classification
- Database-backed audit logging
- Role-based access control
- Production deployment