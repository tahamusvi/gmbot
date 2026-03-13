from flask import Flask, request, jsonify
import google.generativeai as genai
import requests
import os
import concurrent.futures  # اضافه شدن کتابخونه مدیریت زمان

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

# تابعی که فقط وظیفه حرف زدن با هوش مصنوعی رو داره
def get_ai_response(text):
    return model.generate_content(text).text

@app.route('/', methods=['POST', 'GET'])
def webhook():
    if request.method == 'POST':
        update = request.get_json()
        
        if "message" in update and "text" in update["message"]:
            chat_id = update["message"]["chat"]["id"]
            user_text = update["message"]["text"]

            try:
                # اجرای تابع با محدودیت زمانی ۸ ثانیه
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(get_ai_response, user_text)
                    # اگر تو 8 ثانیه جواب نیومد، ارور TimeoutError میده
                    bot_reply = future.result(timeout=8) 
                    
            except concurrent.futures.TimeoutError:
                # این ارور رو خودمون قبل از ورسل شکار می‌کنیم
                bot_reply = "⏱ **ارور تایم‌اوت:** استاد در حال نوشتن یک جواب طولانی و تحلیلی بود که سرور رایگان ورسل زمان رو قطع کرد! لطفاً سوالت رو خردتر بپرس (مثلاً به جای «کلیدها رو توضیح بده»، بپرس «کلید خارجی (FK) چیست؟»)."
            except Exception as e:
                bot_reply = f"❌ ارور سیستم:\n{str(e)}"

            send_message(chat_id, bot_reply)
            
        return jsonify({"status": "ok"})
    
    return "Bot Server is Running on Vercel!"