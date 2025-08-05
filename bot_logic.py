from ai_agent import summarize_and_extract_meeting, is_meeting_email
from gmail_api import get_recent_emails
from calendar_api import create_event

def process_latest_email():
    emails = get_recent_emails(max_results=1)
    if not emails:
        return {"status": "No emails found"}

    email = emails[0]

    # ✅ AI checks if it's a meeting
    if not is_meeting_email(email):
        summary, _ = summarize_and_extract_meeting(email)
        return {
            "summary": summary,
            "meeting_info": None,
            "event_link": "Not a meeting email - no event created"
        }

    # ✅ Proceed if AI confirms it's a meeting
    summary, meeting_info = summarize_and_extract_meeting(email)
    event_link = create_event(meeting_info["title"], meeting_info["date"], meeting_info["time"]) if meeting_info else None

    return {
        "summary": summary,
        "meeting_info": meeting_info,
        "event_link": event_link or "Event creation failed"
    }
