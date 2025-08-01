from gmail_api import get_recent_emails
from ai_agent import summarize_and_extract_meeting
from calendar_api import create_event

if __name__ == "__main__":
    emails = get_recent_emails()
    print(f"Fetched Emails: {len(emails)}")

    for i, email in enumerate(emails):
        print(f"\n--- Email {i+1} ---")
        summary, info = summarize_and_extract_meeting(email)
        print("AI Summary:", summary)
        print("Meeting Info:", info)

        if info["date"] and info["time"]:
            create_event(info["title"], info["date"], info["time"])
