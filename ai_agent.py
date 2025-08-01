import requests, os, re, json
from dotenv import load_dotenv
from dateutil import parser
import dateparser
from dateparser.search import search_dates

load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")

SUMMARIZER_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
QA_URL = "https://api-inference.huggingface.co/models/deepset/roberta-base-squad2"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

# ---------------- Regex fallback ----------------
def extract_date_time_regex(text):
    clean = text.replace("**", "")
    date_match = re.search(r'(\d{1,2}\s+[A-Za-z]+\s+\d{4})', clean)
    time_match = re.search(r'(\d{1,2}(:\d{2})?\s?(AM|PM|am|pm)?)', clean)

    date, time = None, None
    if date_match:
        try: date = parser.parse(date_match.group(1)).strftime("%Y-%m-%d")
        except: pass
    if time_match:
        try: time = parser.parse(time_match.group(1)).strftime("%H:%M")
        except: pass
    return date, time

# ---------------- AI Q&A extractor ----------------
def ai_extract_meeting_info(email_text):
    def ask(q, ctx):
        payload = {"inputs": {"question": q, "context": ctx}}
        res = requests.post(QA_URL, headers=headers, json=payload).json()
        print(f"[DEBUG] Q&A Response for '{q}':", res)
        return res.get('answer', None)

    date_ai = ask("When is the meeting?", email_text)
    time_ai = ask("At what time is the meeting?", email_text)
    location_ai = ask("Where is the meeting?", email_text)
    title_ai = ask("What is the meeting about?", email_text)

    # --- parse natural date ---
    parsed_date = None
    if date_ai:
        d = dateparser.parse(date_ai)
        if d: parsed_date = d.strftime("%Y-%m-%d")

    if not parsed_date:
        found = search_dates(email_text)
        if found: parsed_date = found[0][1].strftime("%Y-%m-%d")

    # --- location filtering ---
    if location_ai and re.search(r"\d{4}", location_ai):
        location_ai = "Online"

    return {
        "title": title_ai if title_ai and "office" not in title_ai.lower() else "Meeting",
        "date": parsed_date,
        "time": time_ai,
        "location": location_ai or "Online"
    }

# ---------------- Summarizer ----------------
def summarize_email(text):
    payload = {"inputs": text}
    r = requests.post(SUMMARIZER_URL, headers=headers, json=payload).json()
    print("[DEBUG] Summarizer Response:", r)
    return r[0]['summary_text'] if isinstance(r, list) else "Could not summarize"

# ---------------- Final Wrapper ----------------
def summarize_and_extract_meeting(email_text):
    summary = summarize_email(email_text)
    info = ai_extract_meeting_info(email_text)

    # fallback for date/time
    if not info["date"] or not info["time"]:
        d, t = extract_date_time_regex(email_text)
        if d: info["date"] = d
        if t: info["time"] = t

    # normalize time
    if info["time"]:
        try: info["time"] = dateparser.parse(info["time"]).strftime("%H:%M")
        except: info["time"] = "09:00"

    return summary, info



