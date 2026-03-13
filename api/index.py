import telebot
import google.generativeai as genai
import os
import threading
from flask import Flask

# دریافت کلیدها از Environment Variables رندر
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# کانفیگ هوش مصنوعی
genai.configure(api_key=GEMINI_API_KEY)

# پرامپت استراتژیک کنکور ارشد (Hit & Run)
system_prompt = """تو یک استاد مسلط و دقیق کنکور ارشد مهندسی کامپیوتر هستی. 
هدف کاربر: کسب ۳۰ الی ۳۵ درصد (حدود ۳۰ تست درست) برای قبولی در دانشگاه تهران یا امیرکبیر.
دروس مورد تمرکز: سیستم‌عامل، شبکه، پایگاه داده، هوش مصنوعی، ساختمان داده، مدار منطقی و نظریه زبان‌ها.
لحن: جدی، تحلیلی، کنکوری و متمرکز بر نکات تستی.
پاسخ‌ها را بدون محدودیت طولانی، با جزئیات کامل و به صورت کاملاً تشریحی ارائه بده."""

generation_config = genai.types.GenerationConfig(temperature=0.2)
model = genai.GenerativeModel(
    model_name='gemini-2.5-flash',
    system_instruction=system_prompt,
    generation_config=generation_config
)

# راه‌اندازی ربات تلگرام
bot = telebot.TeleBot(TELEGRAM_TOKEN)

def send_long_message(chat_id, text, reply_to_id):
    """تابع کمکی برای تیکه‌تیکه کردن پیام‌های بسیار طولانی"""
    if len(text) <= 4000:
        bot.send_message(chat_id, text, reply_to_message_id=reply_to_id)
    else:
        for i in range(0, len(text), 4000):
            bot.send_message(chat_id, text[i:i+4000])

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    # نشان دادن وضعیت Typing در تلگرام
    bot.send_chat_action(message.chat.id, 'typing')
    
    try:
        # ارسال سوال به مدل و دریافت پاسخ
        response = model.generate_content(message.text)
        bot_reply = response.text
        
        # ارسال پاسخ نهایی
        send_long_message(message.chat.id, bot_reply, message.message_id)
        
    except Exception as e:
        bot.reply_to(message, f"❌ خطای سیستم:\n{str(e)}")

# --- بخش Flask برای زنده نگه داشتن سرور در Render ---
app = Flask(__name__)

@app.route('/')
def health_check():
    return "استاد آنلاین است و آماده پاسخگویی به سوالات کنکور!"

def run_flask():
    port = int(os.environ.get('PORT', 5000))
    app.run(host="0.0.0.0", port=port)

# --- اجرای همزمان سرور وب و ربات تلگرام ---
if __name__ == "__main__":
    # اجرای Flask در یک ترد جداگانه
    threading.Thread(target=run_flask, daemon=True).start()
    
    print("Bot is polling and ready for Master's exam prep...")
    # اجرای Polling ربات در ترد اصلی
    bot.polling(none_stop=True)