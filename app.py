import json

from classifier import classify_email
from actions import determine_action
from audit import save_audit


def load_emails():
    with open("data/emails.json", "r", encoding="utf-8") as file:
        return json.load(file)


def process_email(email, processed_emails):

    # 1. Classify the email
    classification = classify_email(email)

    # 2. Determine and execute action
    result = determine_action(
        email,
        classification,
        processed_emails=processed_emails
    )

    # 3. Record audit trail
    save_audit(
        email,
        classification,
        result["action"],
        result
    )

    return classification, result


def main():

    emails = load_emails()

    # Stores fingerprints/keys of already processed emails
    processed_emails = set()

    print("\n" + "=" * 70)
    print("SMART MAIL OPS")
    print("Autonomous Email-to-Action Agent")
    print("=" * 70)

    for email in emails:

        classification, result = process_email(
            email,
            processed_emails
        )

        print("\nEmail:", email["id"])
        print("Subject:", email["subject"])
        print("Intent:", classification["intent"])
        print(
            "Confidence:",
            f"{classification['confidence'] * 100:.0f}%"
        )
        print("Reason:", classification["reason"])
        print("Action:", result["action"])
        print("Result:", result["result"])
        print("Automated:", result.get("automated"))
        print("Duplicate:", result.get("duplicate"))

        print("-" * 70)


if __name__ == "__main__":
    main()