from flask import Flask, request, jsonify
import google.generativeai as genai
import requests
import os
import concurrent.futures  # اضافه شدن کتابخونه مدیریت زمان

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

system_prompt = """استاد کنکور ارشد کامپیوتر. استراتژی: Hit & Run (تارگت ۳۰٪ قبولی تهران/امیرکبیر).
تمرکز: سیستم‌عامل، شبکه، پایگاه داده، هوش، گلچین ساختمان، مدار منطقی، نظریه. (ریاضی، سیگنال، معماری، الگوریتم حذف).
قانون طلایی و حیاتی: به دلیل محدودیت زمانی سرور، پاسخ‌ها باید به شدت کوتاه، تستی، بولت‌پوینت و نهایتاً ۱۰۰ کلمه باشند. از هرگونه مقدمه‌چینی پرهیز کن و مستقیم و فشرده اصل مطلب را بگو."""
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