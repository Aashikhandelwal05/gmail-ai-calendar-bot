from flask import Flask, render_template, jsonify
from bot_logic import process_latest_email

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/run-bot")
def run_bot():
    result = process_latest_email()
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
