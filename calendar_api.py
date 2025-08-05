from __future__ import print_function
import datetime
from datetime import datetime, timedelta
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/calendar.events']

def get_calendar_service():
    """Authenticate and return Google Calendar service"""
    creds = None
    if os.path.exists('token_calendar.pickle'):
        with open('token_calendar.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token_calendar.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return build('calendar', 'v3', credentials=creds)

def normalize_time(time):
    """Convert AI extracted time like '2 PM' or '14:00' to '%H:%M' format"""
    if not time:
        return "09:00"
    try:
        return datetime.strptime(time, "%I %p").strftime("%H:%M")  # '2 PM'
    except:
        try:
            return datetime.strptime(time, "%H:%M").strftime("%H:%M")  # '14:00'
        except:
            return "09:00"

def create_event(title, date, time):
    """Create Google Calendar event and return event link"""
    service = get_calendar_service()  # ✅ FIX: Authenticate here

    if not date:
        date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    time_24 = normalize_time(time)
    start_str = f"{date} {time_24}"
    start = datetime.strptime(start_str, "%Y-%m-%d %H:%M")
    end = start + timedelta(hours=1)

    event = {
        'summary': title,
        'start': {'dateTime': start.isoformat(), 'timeZone': 'Asia/Kolkata'},
        'end': {'dateTime': end.isoformat(), 'timeZone': 'Asia/Kolkata'},
    }

    event_result = service.events().insert(calendarId='primary', body=event).execute()
    print(f"✅ Event created: {event_result.get('htmlLink')}")
    return event_result.get('htmlLink')

