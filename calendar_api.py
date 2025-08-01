from __future__ import print_function
from datetime import datetime, timedelta
import os.path, pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/calendar.events']

# --- Auth ---
def authenticate_calendar():
    creds = None
    if os.path.exists('token_calendar.pickle'):
        with open('token_calendar.pickle', 'rb') as t:
            creds = pickle.load(t)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token_calendar.pickle', 'wb') as t:
            pickle.dump(creds, t)
    return build('calendar', 'v3', credentials=creds)

# --- Normalize Time ---
def normalize_time(t):
    if not t: return "09:00"
    try: return datetime.strptime(t, "%I %p").strftime("%H:%M")
    except:
        try: return datetime.strptime(t, "%H:%M").strftime("%H:%M")
        except: return "09:00"

# --- Create Event ---
def create_event(title, date, time):
    service = authenticate_calendar()
    if not date: date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    time_24 = normalize_time(time)
    start_dt = datetime.strptime(f"{date} {time_24}", "%Y-%m-%d %H:%M")
    end_dt = start_dt + timedelta(hours=1)

    event = {
        'summary': title,
        'start': {'dateTime': start_dt.isoformat(), 'timeZone': 'Asia/Kolkata'},
        'end': {'dateTime': end_dt.isoformat(), 'timeZone': 'Asia/Kolkata'},
    }

    e = service.events().insert(calendarId='primary', body=event).execute()
    print(f"✅ Event created: {e.get('htmlLink')}")
