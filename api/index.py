import telebot
import google.generativeai as genai
import os
import threading
from flask import Flask

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
genai.configure(api_key=GEMINI_API_KEY)

# پرامپت رو کامل‌تر کردم چون اینجا دیگه مشکل تایم‌اوت نداریم
system_prompt = """استاد کنکور ارشد کامپیوتر. استراتژی: Hit & Run (تارگت ۳۰٪ قبولی تهران/امیرکبیر).
تمرکز: سیستم‌عامل، شبکه، پایگاه داده، هوش، گلچین ساختمان، مدار منطقی، نظریه. (ریاضی، سیگنال، معماری، الگوریتم حذف).
توضیحاتت باید دقیق، کنکوری، جامع و با رویکرد حل تست باشد و هر چقدر نیاز است طولانی باشد."""

generation_config = genai.types.GenerationConfig(temperature=0.2)
model = genai.GenerativeModel(
    model_name='gemini-2.5-flash',
    system_instruction=system_prompt,
    generation_config=generation_config
)

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    bot.send_chat_action(message.chat.id, 'typing')
    try:
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text, parse_mode='Markdown')
    except Exception as e:
        bot.reply_to(message, f"❌ ارور: {str(e)}")

# ------ بخش سرور مجازی برای زنده نگه داشتن سرور رندر ------
app = Flask(__name__)
@app.route('/')
def index():
    return "Bot is alive and running on Render!"

def run_web():
    port = int(os.environ.get('PORT', 5000))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web).start()
# ------------------------------------------------------------

print("Bot is polling...")
bot.polling(none_stop=True)