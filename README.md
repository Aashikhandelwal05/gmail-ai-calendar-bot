# 🚀 AI Email-to-Calendar Automation

An **AI-powered automation tool** that reads Gmail emails, extracts meeting details using NLP, and automatically schedules events in Google Calendar.

---

## ✨ Features
- ✅ Fetches the latest emails from Gmail  
- ✅ Summarizes emails using **HuggingFace BART**  
- ✅ Extracts meeting details (date, time, location, title) using **RoBERTa Q&A**  
- ✅ Falls back to regex and dateparser for robust extraction  
- ✅ Automatically creates events in Google Calendar via API  
- ✅ Secure authentication with OAuth 2.0  
- ✅ Can be extended to run as a web service or background job  

---

## 🛠️ Tech Stack
- **Python**
- **HuggingFace Transformers API**
- **Google Gmail API**
- **Google Calendar API**
- **OAuth 2.0**
- **Regex + Dateparser**

---

## 📂 Project Structure
AgenticAI/
│ app.py # Main entry point
│ gmail_api.py # Gmail API integration
│ ai_agent.py # AI logic (summarization + meeting extraction)
│ calendar_api.py # Google Calendar API integration
│ requirements.txt # Dependencies
│ .env # HuggingFace API key (not uploaded)
│ .gitignore # Ignore secrets/tokens
└─── pycache/ # Auto-generated



---

## ⚡ How It Works
1. Authenticates with Gmail & Calendar (OAuth 2.0)  
2. Fetches recent emails  
3. Summarizes content using **BART**  
4. Extracts meeting details with **RoBERTa Q&A**  
5. Creates events in Google Calendar automatically  

---

## 🖥️ Setup Instructions

### 1️⃣ Clone the repository
```bash
git clone https://github.com/yourusername/gmail-ai-calendar-bot.git
cd gmail-ai-calendar-bot

### 2️⃣ Install dependencies
```bash
pip install -r requirements.txt

### 3️⃣ Add HuggingFace Token

HF_TOKEN=your_huggingface_api_token_here

###4️⃣ Set up Google APIs
1) Enable Gmail API & Google Calendar API on Google Cloud Console.

2) Download credentials.json and place it in the project root.

###5️⃣ Run the App
```bash
python app.py

###🚀 Future Improvements
🔹 Deploy as a background service (auto-check emails periodically)

🔹 Web interface for easier client use

🔹 Support for multiple email accounts

