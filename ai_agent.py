import requests, os, re, json
from dotenv import load_dotenv
from dateutil import parser
import dateparser
from dateparser.search import search_dates

load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")

# HuggingFace API endpoints
SUMMARIZER_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
QA_URL = "https://api-inference.huggingface.co/models/deepset/roberta-base-squad2"
CLASSIFIER_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"

headers = {"Authorization": f"Bearer {HF_TOKEN}"}

# ---------------- Regex fallback ----------------
def extract_date_time_regex(text):
    clean = text.replace("**", "")
    date_match = re.search(r'(\d{1,2}\s+[A-Za-z]+\s+\d{4})', clean)
    time_match = re.search(r'(\d{1,2}(:\d{2})?\s?(AM|PM|am|pm)?)', clean)

    date, time = None, None
    if date_match:
        try:
            date = parser.parse(date_match.group(1)).strftime("%Y-%m-%d")
        except:
            pass
    if time_match:
        try:
            time = parser.parse(time_match.group(1)).strftime("%H:%M")
        except:
            pass
    return date, time

# ---------------- AI Meeting Classifier ----------------
def is_meeting_email(text):
    """Hybrid approach: AI classification + keyword cross-check."""
    payload = {
        "inputs": text,
        "parameters": {"candidate_labels": ["meeting", "not a meeting"]}
    }
    res = requests.post(CLASSIFIER_URL, headers=headers, json=payload).json()
    print("[DEBUG] Classifier Response:", res)

    # Default fallback
    if "labels" not in res or "scores" not in res:
        return False

    top_label = res["labels"][0]
    confidence = res["scores"][0]

    # Keyword backup check
    keywords = ["meeting", "schedule", "invite", "appointment", "zoom", "google meet", "conference", "call"]
    has_keyword = any(word in text.lower() for word in keywords)

    print(f"[DEBUG] Prediction: {top_label}, Confidence: {confidence:.2f}, KeywordFound: {has_keyword}")

    # ✅ Only allow meetings if AI confidence is high OR both AI low confidence + keywords present
    return (top_label == "meeting" and confidence > 0.80) or (has_keyword and confidence > 0.65)
def is_meeting_email(text):
    """Hybrid approach: AI classification + keyword cross-check."""
    payload = {
        "inputs": text,
        "parameters": {"candidate_labels": ["meeting", "not a meeting"]}
    }
    res = requests.post(CLASSIFIER_URL, headers=headers, json=payload).json()
    print("[DEBUG] Classifier Response:", res)

    # Default fallback
    if "labels" not in res or "scores" not in res:
        return False

    top_label = res["labels"][0]
    confidence = res["scores"][0]

    # Keyword backup check
    keywords = ["meeting", "schedule", "invite", "appointment", "zoom", "google meet", "conference", "call"]
    has_keyword = any(word in text.lower() for word in keywords)

    print(f"[DEBUG] Prediction: {top_label}, Confidence: {confidence:.2f}, KeywordFound: {has_keyword}")

    # ✅ Only allow meetings if AI confidence is high OR both AI low confidence + keywords present
    return (top_label == "meeting" and confidence > 0.80) or (has_keyword and confidence > 0.65)

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
        if d:
            parsed_date = d.strftime("%Y-%m-%d")
    if not parsed_date:
        found = search_dates(email_text)
        if found:
            parsed_date = found[0][1].strftime("%Y-%m-%d")

    # --- location fallback ---
    if location_ai and re.search(r"\d{4}", location_ai):
        location_ai = "Online"

    return {
        "title": title_ai if title_ai and "office" not in title_ai.lower() else "Meeting",
        "date": parsed_date,
        "time": time_ai,
        "location": location_ai or "Online"
    }

# ---------------- AI Summarizer ----------------
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
        try:
            info["time"] = dateparser.parse(info["time"]).strftime("%H:%M")
        except:
            info["time"] = "09:00"

    return summary, info


