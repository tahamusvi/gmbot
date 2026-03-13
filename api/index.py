import telebot
import google.generativeai as genai
import os

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# راه‌اندازی ربات و هوش مصنوعی
bot = telebot.TeleBot(TELEGRAM_TOKEN)
genai.configure(api_key=GEMINI_API_KEY)

system_prompt = """تو یک استاد سخت‌گیر، دقیق و مسلط به کنکور ارشد مهندسی کامپیوتر و نرم‌افزار هستی.
هدف کاربر اجرای استراتژی Hit & Run برای شکار حدود ۳۰ تا ۳۳ تست جهت تضمین قبولی در دانشگاه‌های تاپ مثل تهران و امیرکبیر است.
نقاط قوت و تمرکز اصلی: سیستم‌عامل، شبکه، پایگاه داده، هوش مصنوعی، گلچین ساختمان داده، مدار منطقی و نظریه زبان‌ها.
پاسخ‌هایت باید با جزئیات کاملِ علمی، با رویکرد حل تست، و کاملاً دقیق باشد تا در دام‌های تستی نیفتد."""

generation_config = genai.types.GenerationConfig(temperature=0.2)
model = genai.GenerativeModel(
    model_name='gemini-2.5-flash',
    system_instruction=system_prompt,
    generation_config=generation_config
)

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    # نمایش وضعیت "در حال تایپ..." در تلگرام
    bot.send_chat_action(message.chat.id, 'typing')
    
    try:
        # دریافت جواب از مدل (بدون هیچ محدودیت زمانی)
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text, parse_mode='Markdown')
    except Exception as e:
        bot.reply_to(message, f"❌ ارور: {str(e)}")

print("Bot is running...")
bot.polling(none_stop=True)