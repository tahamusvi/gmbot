from flask import Flask, request, jsonify
import google.generativeai as genai
import requests
import os

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

system_prompt = """تو یک استاد سخت‌گیر، دقیق و مسلط به کنکور ارشد مهندسی کامپیوتر و نرم‌افزار هستی.
هدف کاربر اجرای استراتژی Hit & Run برای شکار حدود ۳۰ تا ۳۳ تست (تارگت ۳۰ الی ۳۵ درصد) جهت تضمین قبولی در دانشگاه‌های تاپ مثل تهران و امیرکبیر است.
نقاط قوت و تمرکز اصلی باید روی پاسخ‌گویی دقیق، تستی و تحلیلی به دروس زیر باشد: 
سیستم‌عامل، شبکه، پایگاه داده (به عنوان موتور رتبه‌ساز)، هوش مصنوعی، گلچین ساختمان داده، مدار منطقی و نظریه زبان‌ها.
دروس ریاضیات، سیگنال، معماری و الکترونیک دیجیتال و الگوریتم کلا حذف شده‌اند.
پاسخ‌هایت باید بدون حاشیه‌روی، با جزئیات کاملِ علمی، با رویکرد حل تست، و کاملاً دقیق باشد تا در دام‌های تستی نیفتد."""

generation_config = genai.types.GenerationConfig(temperature=0.2)

model = genai.GenerativeModel(
    model_name='gemini-2.5-flash',
    system_instruction=system_prompt,
    generation_config=generation_config
)

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

@app.route('/', methods=['POST', 'GET'])
def webhook():
    if request.method == 'POST':
        update = request.get_json()
        
        if "message" in update and "text" in update["message"]:
            chat_id = update["message"]["chat"]["id"]
            user_text = update["message"]["text"]

            try:
                response = model.generate_content(user_text)
                bot_reply = response.text
            except Exception as e:
                # هک جذاب: گرفتن لیست مدل‌های مجاز در صورت بروز خطا
                bot_reply = f"❌ ارور سیستم:\n{str(e)}\n\n"
                try:
                    models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                    bot_reply += "✅ لیست مدل‌هایی که کلید شما پشتیبانی می‌کند:\n" + "\n".join(models)
                except Exception as inner_e:
                    bot_reply += f"خطا در دریافت لیست مدل‌ها: {str(inner_e)}"

            send_message(chat_id, bot_reply)
            
        return jsonify({"status": "ok"})
    
    return "Bot Server is Running on Vercel!"