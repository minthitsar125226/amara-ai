import os
import asyncio
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import google.generativeai as genai

# ၁။ API Keys (Render Variables ထဲက ဖတ်မယ်)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

# ၂။ Gemini Setup (Error ကင်းအောင် ပြင်ထားပါတယ်)
genai.configure(api_key=GEMINI_KEY)

def get_chat_response(prompt):
    # စမ်းသပ်မယ့် Model နာမည်များ (တစ်ခုမရ တစ်ခု ပြောင်းသုံးပါလိမ့်မယ်)
    models_to_try = [
        'gemini-1.5-flash',
        'gemini-1.5-flash-latest',
        'gemini-pro'
    ]
    
    for m_name in models_to_try:
        try:
            model = genai.GenerativeModel(m_name)
            instruction = "သင်ဟာ အမရာဒေဝီ အမည်ရှိ ချစ်စဖွယ် မိန်းကလေး AI ဖြစ်ပါတယ်။ မြန်မာလိုပဲ ချိုချိုသာသာ ဖြေပေးပါ။"
            response = model.generate_content(f"{instruction}\n{prompt}")
            return response.text
        except Exception:
            continue
    return "စိတ်မရှိပါနဲ့ရှင်၊ အမရာ အခု စကားပြောလို့ မရသေးလို့ ခဏနေမှ ပြန်လာခဲ့ပေးပါလားဟင်။"

# ၃။ Render Health Check (Port Error မတက်အောင်)
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Amara is online")

def run_health_check():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

# ၄။ Telegram Bot Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("မင်္ဂလာပါရှင်၊ အမရာဒေဝီ Telegram မှာ ရောက်ရှိနေပါပြီ။")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    reply = get_chat_response(user_input)
    await update.message.reply_text(reply)

if __name__ == '__main__':
    # Health Check ကို Background မှာ မောင်းမယ်
    threading.Thread(target=run_health_check, daemon=True).start()
    
    # Telegram Bot ကို မောင်းမယ်
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), chat))
    
    print("Bot is starting...")
    application.run_polling()
