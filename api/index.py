from flask import Flask, request, jsonify
import google.generativeai as genai
import requests
import os

app = Flask(__name__)

# گرفتن کلیدها از متغیرهای محیطی (Environment Variables)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# تنظیمات API من (Gemini)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro')

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

@app.route('/', methods=['POST', 'GET'])
def webhook():
    if request.method == 'POST':
        update = request.get_json()
        
        # بررسی اینکه آیا پیامی دریافت شده یا نه
        if "message" in update and "text" in update["message"]:
            chat_id = update["message"]["chat"]["id"]
            user_text = update["message"]["text"]

            try:
                # ارسال متن به Gemini و دریافت جواب
                response = model.generate_content(user_text)
                bot_reply = response.text
            except Exception as e:
                # ارسال متن دقیق ارور به داخل چت تلگرام
                bot_reply = f"❌ ارور سیستم:\n{str(e)}"

            # ارسال جواب به کاربر در تلگرام
            send_message(chat_id, bot_reply)
            
        return jsonify({"status": "ok"})
    
    return "Bot Server is Running on Vercel!"


# for deploy